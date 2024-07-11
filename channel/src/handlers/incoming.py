import json
import logging
import base64
from ..crud import (
    get_channel_by_session_id,
    set_user_language,
    update_message,
)
from lib.data_models import (
    BotInput,
    ChannelData,
    ChannelInput,
    FlowInput,
    LanguageInput,
    LanguageIntent,
    MessageData,
    MessageType,
)
from lib.model import Language
from lib.whatsapp import WhatsappHelper, WAMsgType
from lib.file_storage import StorageHandler
from lib.encryption_handler import EncryptionHandler

logging.basicConfig()
logger = logging.getLogger("channel")
logger.setLevel(logging.INFO)

storage = StorageHandler.get_async_instance()


async def process_incoming_messages(message: ChannelInput):
    """Process incoming messages"""
    msg_id: str = message.message_id
    turn_id = message.turn_id
    session_id: str = message.session_id
    bot_input: ChannelData = message.channel_data
    message_type = bot_input.type

    recieved_message = None
    logger.info("Message type: %s", message_type)
    if message_type == MessageType.TEXT:
        recieved_message = WhatsappHelper.wa_get_user_text(bot_input)
        await update_message(msg_id, message_text=recieved_message.content)
    if message_type == MessageType.AUDIO:
        channel_details = await get_channel_by_session_id(session_id=session_id)
        if not channel_details:
            logger.error("Channel details not found")
            return None
        wa_bnumber: str = channel_details.app_id
        wa_api_key: str = channel_details.key
        wa_api_key = EncryptionHandler.decrypt_text(wa_api_key)
        recieved_message = WhatsappHelper.wa_get_user_audio(
            wa_bnumber=wa_bnumber, wa_api_key=wa_api_key, msg_obj=bot_input
        )
        audio_bytes = base64.b64decode(recieved_message.content)
        audio_file_name = f"{msg_id}.ogg"
        logger.info("audio_file_name: %s", audio_file_name)
        await storage.write_file(audio_file_name, audio_bytes, "audio/ogg")
        storage_url = await storage.public_url(audio_file_name)
        recieved_message.content = storage_url
        await update_message(msg_id, media_url=storage_url)
    if message_type == MessageType.INTERACTIVE:
        recieved_message = WhatsappHelper.wa_get_interactive_reply(bot_input)
        logger.info("Got an interactive block")
    if message_type == MessageType.FORM:
        recieved_message = WhatsappHelper.wa_get_form_reply(bot_input)
        logger.info("Got a form block")

    logger.info("Got a message: %s", recieved_message)
    if recieved_message:
        if (
            recieved_message.msgtype == WAMsgType.interactive
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
            return flow_input

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
                return whatsapp_data
            else:
                form_data = json.loads(recieved_message.content)
                flow_data = FlowInput(
                    source="channel",
                    session_id=session_id,
                    message_id=msg_id,
                    turn_id=turn_id,
                    intent=LanguageIntent.LANGUAGE_IN,
                    form_response=form_data,
                )
                return flow_data
