import asyncio
import base64
import json
import os
import logging
import traceback
from dotenv import load_dotenv
from lib.utils import decrypt_credentials
from crud import (
    get_user_by_session_id,
    get_channel_by_session_id,
    set_user_language,
    update_message,
    create_message,
)
from lib.data_models import (
    BotInput,
    ChannelData,
    BotOutput,
    ChannelInput,
    ChannelIntent,
    FlowInput,
    LanguageInput,
    LanguageIntent,
    MessageData,
    MessageType,
)
from lib.kafka_utils import KafkaConsumer, KafkaProducer
from lib.azure_storage import AzureStorage
from lib.model import Language
from lib.utils import decrypt_credentials
from lib.channel_handler import ChannelHandler
from lib.whatsapp_helper import WhatsappHelper
from lib.custom_channel_helper import CustomChannelHelper

load_dotenv()

logging.basicConfig()
logger = logging.getLogger("channel")
logger.setLevel(logging.INFO)

azure_creds = {
    "account_url": os.getenv("STORAGE_ACCOUNT_URL"),
    "account_key": os.getenv("STORAGE_ACCOUNT_KEY"),
    "container_name": os.getenv("STORAGE_AUDIOFILES_CONTAINER"),
    "base_path": "input/",
}
storage = AzureStorage(**azure_creds)

channel_topic = os.getenv("KAFKA_CHANNEL_TOPIC")
language_topic = os.getenv("KAFKA_LANGUAGE_TOPIC")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")

logger.info("Connecting to kafka topic: %s", channel_topic)
consumer = KafkaConsumer.from_env_vars(
    group_id="cooler_group_id", auto_offset_reset="latest"
)
logger.info("Connected to kafka topic: %s", channel_topic)

logger.info("Connecting to kafka topic: %s", language_topic)
producer = KafkaProducer.from_env_vars()
logger.info("Connected to kafka topic: %s %s", language_topic, flow_topic)
channel_map = {"Whatsapp": WhatsappHelper, "custom": CustomChannelHelper}


async def process_incoming_messages(message: ChannelInput):
    """Process incoming messages"""
    msg_id = message.message_id
    turn_id = message.turn_id
    session_id = message.session_id
    bot_input: ChannelData = message.channel_data
    channel = await get_channel_by_session_id(session_id=session_id)
    message_type = bot_input.type
    channel_helper: ChannelHandler = channel_map[channel.type]

    recieved_message = None
    logger.info("Message type: %s", message_type)
    recieved_message = await channel_helper.to_bot_input(channel, msg_id, bot_input)
    await update_message(msg_id, message_text=recieved_message.content)

    logger.info("Got a message: %s", recieved_message)
    if recieved_message:
        if (
            recieved_message.msgtype == MessageType.INTERACTIVE
            and recieved_message.content.startswith("lang_")
        ):
            selected_language = recieved_message.content
            language_dict = {
                "lang_hindi": "Hindi",
                "lang_bengali": "Bengali",
                "lang_telugu": "Telugu",
                "lang_marathi": "Marathi",
                "lang_tamil": "Tamil",
                "lang_gujarati": "Gujarati",
                "lang_urdu": "Urdu",
                "lang_kannada": "Kannada",
                "lang_odia": "Odia",
                "lang_english": "English",
            }
            selected_language = language_dict[selected_language]
            lang = Language(selected_language).name.lower()
            await set_user_language(session_id=session_id, language=lang)
            flow_input = FlowInput(
                source="channel",
                session_id=session_id,
                message_id=msg_id,
                turn_id=turn_id,
                intent=LanguageIntent.LANGUAGE_IN,
                dialog="language_selected",
            )
            producer.send_message(
                flow_topic, flow_input.model_dump_json(exclude_none=True)
            )

        else:
            if message_type != MessageType.FORM:
                if message_type == MessageType.AUDIO:
                    message_data = MessageData(
                        message_text="",
                        media_url=recieved_message.content,
                    )
                else:
                    message_data = MessageData(message_text=recieved_message.content)

                logger.info("Message data: %s", message_data)
                logger.info("Message type: %s", message_type)

                whatsapp_data = LanguageInput(
                    source="channel",
                    session_id=session_id,
                    message_id=msg_id,
                    turn_id=turn_id,
                    intent=LanguageIntent.LANGUAGE_IN,
                    data=BotInput(
                        message_type=message_type,
                        message_data=message_data,
                    ),
                )
                producer.send_message(
                    language_topic, whatsapp_data.model_dump_json(exclude_none=True)
                )
            else:
                form_data = json.loads(recieved_message.content)
                flow_data = FlowInput(
                    source="channel",
                    session_id=session_id,
                    message_id=msg_id,
                    turn_id=turn_id,
                    intent=LanguageIntent.LANGUAGE_IN,
                    # message_type=message_type,
                    form_response=form_data,
                )
                producer.send_message(
                    flow_topic, flow_data.model_dump_json(exclude_none=True)
                )


async def send_message_to_user(message: ChannelInput):
    """Send Message to user"""
    session_id = message.session_id
    bot_output: BotOutput = message.data
    user = await get_user_by_session_id(session_id=session_id)
    channel = await get_channel_by_session_id(session_id=session_id)
    channel_helper = channel_map[channel.type]

    if message.dialog == "language":
        channel_id = channel_helper.wa_send_text_message(
            channel=channel,
            user_tele=user.phone_number,
            text=bot_output.message_data.message_text,
        )
        await create_message(
            turn_id=message.turn_id,
            message_type="text",
            channel=channel.type,
            channel_id=channel_id,
            is_user_sent=False,
            message_text=bot_output.message_data.message_text,
        )
        channel_id = channel_helper.wa_send_interactive_message(
            channel=channel,
            user_tele=user.phone_number,
            message="Please select your preferred language",
            header="Language",
            body="Choose a Language",
            footer="भाषा चुनें",
            menu_selector="चुनें / Select",
            menu_title="भाषाएँ / Languages",
            options=[
                {"id": "lang_hindi", "title": "हिन्दी"},
                {"id": "lang_english", "title": "English"},
                {"id": "lang_bengali", "title": "বাংলা"},
                {"id": "lang_telugu", "title": "తెలుగు"},
                {"id": "lang_marathi", "title": "मराठी"},
                {"id": "lang_tamil", "title": "தமிழ்"},
                {"id": "lang_gujarati", "title": "ગુજરાતી"},
                {"id": "lang_urdu", "title": "اردو"},
                {"id": "lang_kannada", "title": "ಕನ್ನಡ"},
                {"id": "lang_odia", "title": "ଓଡ଼ିଆ"},
            ],
        )
        await create_message(
            turn_id=message.turn_id,
            message_type="interactive",
            channel=channel.type,
            channel_id=channel_id,
            is_user_sent=False,
            message_text="Please select your preferred language",
        )
    else:
        channel_id = channel_helper.send_message(channel=channel, user=user, bot_ouput=bot_output)
        message_text = bot_output.message_data.message_text
        logger.info("Message type: %s", bot_output.message_type)
        await create_message(
                turn_id=message.turn_id,
                message_type=bot_output.message_type,
                channel=channel.type,
                channel_id=channel_id,
                is_user_sent=False,
                message_text=message_text,
            )
    logger.info("Message sent")


async def start_channel():
    """Starts the channel server"""
    logger.info("Starting Listening")
    while True:
        try:
            msg = consumer.receive_message(channel_topic)
            msg = json.loads(msg)
            logger.info("Input received: %s", msg)
            input_data = ChannelInput(**msg)
            logger.info("Input received in object form: %s", input_data)
            if input_data.intent == ChannelIntent.BOT_IN:
                await process_incoming_messages(input_data)
            elif input_data.intent == ChannelIntent.BOT_OUT:
                await send_message_to_user(input_data)
        except Exception as e:
            logger.error("Error %s", e)
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(start_channel())
