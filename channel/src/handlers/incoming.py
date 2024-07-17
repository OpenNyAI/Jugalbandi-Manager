import logging
import base64
from lib.data_models import (
    RestBotInput,
    Flow,
    FlowIntent,
    UserInput,
    Dialog,
    Message,
    MessageType,
    TextMessage,
    AudioMessage,
    Option,
    InteractiveReplyMessage,
    FormReplyMessage,
    DialogMessage,
    DialogOption,
    Language,
    LanguageIntent,
)
from lib.whatsapp import WhatsappHelper
from lib.file_storage import StorageHandler
from lib.encryption_handler import EncryptionHandler
from lib.model import LanguageCodes
from ..crud import get_channel_by_turn_id

logging.basicConfig()
logger = logging.getLogger("channel")
logger.setLevel(logging.INFO)

storage = StorageHandler.get_async_instance()


async def process_incoming_messages(turn_id: str, bot_input: RestBotInput):
    """Process incoming messages"""
    jb_channel = await get_channel_by_turn_id(turn_id)

    data = bot_input.data
    message_type = data["type"]
    message_data = data[message_type]
    if message_type == "text":
        text = message_data["body"]
        message = Message(
            message_type=MessageType.TEXT,
            text=TextMessage(body=text),
        )
    elif message_type == "audio":
        audio_id = message_data["id"]
        wa_bnumber: str = jb_channel.app_id
        wa_api_key: str = jb_channel.key
        wa_api_key = EncryptionHandler.decrypt_text(wa_api_key)
        recieved_message = WhatsappHelper.wa_get_user_audio(
            wa_bnumber=wa_bnumber, wa_api_key=wa_api_key, audio_id=audio_id
        )
        audio_bytes = base64.b64decode(recieved_message)
        audio_file_name = f"{turn_id}.ogg"
        await storage.write_file(audio_file_name, audio_bytes, "audio/ogg")
        storage_url = await storage.public_url(audio_file_name)

        message = Message(
            message_type=MessageType.AUDIO,
            audio=AudioMessage(media_url=storage_url),
        )
    elif message_type == "interactive":
        interactive_type = message_data["type"]
        interactive_message_data = message_data[interactive_type]
        if interactive_type == "button_reply":
            options = [
                Option(
                    option_id=interactive_message_data["id"],
                    option_text=interactive_message_data["title"],
                )
            ]
            message = Message(
                message_type=MessageType.INTERACTIVE_REPLY,
                interactive_reply=InteractiveReplyMessage(options=options),
            )
        elif interactive_type == "list_reply":
            if (selected_language := interactive_message_data["id"]).startswith(
                "lang_"
            ):
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
                lang = LanguageCodes(selected_language).name.lower()
                message = Message(
                    message_type=MessageType.DIALOG,
                    dialog=DialogMessage(
                        dialog_id=DialogOption.LANGUAGE_SELECTED,
                        dialog_input=lang,
                    ),
                )
            else:
                options = [
                    Option(
                        option_id=interactive_message_data["id"],
                        option_text=interactive_message_data["title"],
                    )
                ]
                message = Message(
                    message_type=MessageType.INTERACTIVE_REPLY,
                    interactive_reply=InteractiveReplyMessage(options=options),
                )
        elif interactive_type == "nfm_reply":
            message = Message(
                message_type=MessageType.FORM_REPLY,
                form_reply=FormReplyMessage(
                    form_data=interactive_message_data["response_json"]
                ),
            )
    else:
        return NotImplemented

    logger.info("Got a message: %s", message)
    if message:
        message_type = message.message_type
        logger.info("Message data: %s", message)
        logger.info("Message type: %s", message_type)
        if (
            message_type == MessageType.TEXT
            or message_type == MessageType.AUDIO
            or message_type == MessageType.IMAGE
            or message_type == MessageType.DOCUMENT
        ):
            language_input = Language(
                source="channel",
                turn_id=turn_id,
                intent=LanguageIntent.LANGUAGE_IN,
                message=message,
            )
            return language_input
        else:
            if message_type == MessageType.DIALOG:
                flow_input = Flow(
                    source="channel",
                    intent=FlowIntent.DIALOG,
                    dialog=Dialog(turn_id=turn_id, message=message),
                )
            else:
                flow_input = Flow(
                    source="channel",
                    intent=FlowIntent.USER_INPUT,
                    user_input=UserInput(turn_id=turn_id, message=message),
                )
            return flow_input
