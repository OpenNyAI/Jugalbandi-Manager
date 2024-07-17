from typing import Dict
import logging
from lib.data_models import (
    Message,
    MessageType,
    TextMessage,
    AudioMessage,
    ImageMessage,
    DocumentMessage,
    FormMessage,
    ButtonMessage,
    ListMessage,
    DialogMessage,
    DialogOption,
)
from lib.whatsapp import WhatsappHelper
from lib.encryption_handler import EncryptionHandler
from ..crud import (
    get_user_by_turn_id,
    get_channel_by_turn_id,
    get_form_parameters,
    create_message,
)

logging.basicConfig()
logger = logging.getLogger("channel")
logger.setLevel(logging.INFO)


async def send_message_to_user(turn_id: str, message: Message):
    """Send Message to user"""
    jb_user = await get_user_by_turn_id(turn_id=turn_id)
    if not jb_user:
        logger.error("User not found")
        return None
    jb_channel = await get_channel_by_turn_id(turn_id=turn_id)
    if not jb_channel:
        logger.error("Channel not found")
        return None
    message_type = message.message_type
    logger.info("Sending message of type %s", message_type)
    wa_bnumber: str = jb_channel.app_id
    wa_api_key: str = EncryptionHandler.decrypt_text(jb_channel.key)
    user_identifier: str = jb_user.identifier
    if message_type == MessageType.TEXT:
        if not message.text:
            raise ValueError("Text message not found")
        text_message: TextMessage = message.text
        WhatsappHelper.wa_send_text_message(
            wa_bnumber=wa_bnumber,
            wa_api_key=wa_api_key,
            user_tele=user_identifier,
            text=text_message.body,
        )
    elif message_type == MessageType.AUDIO:
        if not message.audio:
            raise ValueError("Audio message not found")
        audio_message: AudioMessage = message.audio
        WhatsappHelper.wa_send_audio_message(
            wa_bnumber=wa_bnumber,
            wa_api_key=wa_api_key,
            user_tele=user_identifier,
            audio_url=audio_message.media_url,
        )
    elif message_type == MessageType.BUTTON:
        if not message.button:
            raise ValueError("Button message not found")
        button_message: ButtonMessage = message.button
        WhatsappHelper.wa_send_interactive_message(
            wa_bnumber=wa_bnumber,
            wa_api_key=wa_api_key,
            user_tele=user_identifier,
            message=button_message.body,
            header=button_message.header,
            body=button_message.body,
            footer=button_message.footer,
            menu_selector=None,
            menu_title=button_message.body,
            options=[option.model_dump() for option in button_message.options],
        )
    elif message_type == MessageType.OPTION_LIST:
        if not message.option_list:
            raise ValueError("Option list message not found")
        list_message: ListMessage = message.option_list
        WhatsappHelper.wa_send_interactive_message(
            wa_bnumber=wa_bnumber,
            wa_api_key=wa_api_key,
            user_tele=user_identifier,
            message=list_message.body,
            header=list_message.header,
            body=list_message.body,
            footer=list_message.footer,
            menu_selector=list_message.button_text,
            menu_title=list_message.list_title,
            options=[option.model_dump() for option in list_message.options],
        )
    elif message_type == MessageType.IMAGE:
        if not message.image:
            raise ValueError("Image message not found")
        image_message: ImageMessage = message.image
        WhatsappHelper.wa_send_image(
            wa_bnumber=wa_bnumber,
            wa_api_key=wa_api_key,
            user_tele=user_identifier,
            message=image_message.caption,
            media_url=image_message.url,
        )
    elif message_type == MessageType.DOCUMENT:
        if not message.document:
            raise ValueError("Document message not found")
        document_message: DocumentMessage = message.document
        WhatsappHelper.wa_send_document(
            wa_bnumber=wa_bnumber,
            wa_api_key=wa_api_key,
            user_tele=user_identifier,
            document_url=document_message.url,
            document_name=document_message.name,
            caption=document_message.caption,
        )
    elif message_type == MessageType.FORM:
        if not message.form:
            raise ValueError("Form message not found")
        form_message: FormMessage = message.form
        form_id = form_message.form_id
        form_parameters: Dict = await get_form_parameters(
            channel_id=jb_channel.id, form_id=form_id
        )

        WhatsappHelper.wa_send_form(
            wa_bnumber=wa_bnumber,
            wa_api_key=wa_api_key,
            user_tele=user_identifier,
            body=form_message.body,
            footer=form_message.footer,
            form_parameters=form_parameters,
        )
    elif message_type == MessageType.DIALOG:
        if not message.dialog:
            raise ValueError("Dialog message not found")
        dialog_message: DialogMessage = message.dialog
        if dialog_message.dialog_id == DialogOption.LANGUAGE_CHANGE:
            WhatsappHelper.wa_send_interactive_message(
                wa_bnumber=wa_bnumber,
                wa_api_key=wa_api_key,
                user_tele=user_identifier,
                message="Please select your preferred language",
                header="Language",
                body="Choose a Language",
                footer="भाषा चुनें",
                menu_selector="चुनें / Select",
                menu_title="भाषाएँ / Languages",
                options=[
                    {"option_id": "lang_hindi", "option_text": "हिन्दी"},
                    {"option_id": "lang_english", "option_text": "English"},
                    {"option_id": "lang_bengali", "option_text": "বাংলা"},
                    {"option_id": "lang_telugu", "option_text": "తెలుగు"},
                    {"option_id": "lang_marathi", "option_text": "मराठी"},
                    {"option_id": "lang_tamil", "option_text": "தமிழ்"},
                    {"option_id": "lang_gujarati", "option_text": "ગુજરાતી"},
                    {"option_id": "lang_urdu", "option_text": "اردو"},
                    {"option_id": "lang_kannada", "option_text": "ಕನ್ನಡ"},
                    {"option_id": "lang_odia", "option_text": "ଓଡ଼ିଆ"},
                ],
            )
    else:
        return NotImplemented
    await create_message(
        turn_id=turn_id,
        message_type=message.message_type.value,
        is_user_sent=False,
        message=getattr(message, message.message_type.value).model_dump_json(
            exclude_none=True
        ),
    )
    logger.info("Message sent")
