import logging
from ..crud import (
    get_user_by_session_id,
    get_channel_by_session_id,
    create_message,
)
from lib.data_models import (
    BotOutput,
    ChannelInput,
    MessageType,
)
from lib.whatsapp import WhatsappHelper
from lib.encryption_handler import EncryptionHandler

logging.basicConfig()
logger = logging.getLogger("channel")
logger.setLevel(logging.INFO)


async def send_message_to_user(message: ChannelInput):
    """Send Message to user"""
    session_id = message.session_id
    bot_output: BotOutput = message.data
    user = await get_user_by_session_id(session_id=session_id)
    if not user:
        logger.error("User not found")
        return None
    user_identifier: str = user.identifier
    channel_details = await get_channel_by_session_id(session_id=session_id)
    if not channel_details:
        logger.error("Channel details not found")
        return None
    wa_bnumber, wa_api_key = channel_details
    wa_api_key = EncryptionHandler.decrypt_text(wa_api_key)

    if message.dialog == "language":
        channel_id = WhatsappHelper.wa_send_text_message(
            wa_bnumber=wa_bnumber,
            wa_api_key=wa_api_key,
            user_tele=user_identifier,
            text=bot_output.message_data.message_text,
        )
        await create_message(
            turn_id=message.turn_id,
            message_type="text",
            channel="WA",
            channel_id=channel_id,
            is_user_sent=False,
            message_text=bot_output.message_data.message_text,
        )
        channel_id = WhatsappHelper.wa_send_interactive_message(
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
            channel="WA",
            channel_id=channel_id,
            is_user_sent=False,
            message_text="Please select your preferred language",
        )
    else:
        message_text = bot_output.message_data.message_text
        logger.info("Message type: %s", bot_output.message_type)
        if bot_output.message_type == MessageType.TEXT:
            channel_id = WhatsappHelper.wa_send_text_message(
                wa_bnumber=wa_bnumber,
                wa_api_key=wa_api_key,
                user_tele=user_identifier,
                text=message_text,
            )
            await create_message(
                turn_id=message.turn_id,
                message_type="text",
                channel="WA",
                channel_id=channel_id,
                is_user_sent=False,
                message_text=message_text,
            )
        elif bot_output.message_type == MessageType.AUDIO:
            media_url = bot_output.message_data.media_url
            channel_id = WhatsappHelper.wa_send_audio_message(
                wa_bnumber=wa_bnumber,
                wa_api_key=wa_api_key,
                user_tele=user_identifier,
                audio_url=media_url,
            )
            await create_message(
                turn_id=message.turn_id,
                message_type="audio",
                channel="WA",
                channel_id=channel_id,
                is_user_sent=False,
                media_url=media_url,
            )
        elif bot_output.message_type == MessageType.INTERACTIVE:
            channel_id = WhatsappHelper.wa_send_interactive_message(
                wa_bnumber=wa_bnumber,
                wa_api_key=wa_api_key,
                user_tele=user_identifier,
                message=message_text,
                header=bot_output.header,
                body=message_text,
                footer=bot_output.footer,
                menu_selector=bot_output.menu_selector,
                menu_title=bot_output.menu_title,
                options=(
                    [option.model_dump() for option in bot_output.options_list]
                    if bot_output.options_list
                    else None
                ),
                media_url=bot_output.message_data.media_url,
            )
            await create_message(
                turn_id=message.turn_id,
                message_type="interactive",
                channel="WA",
                channel_id=channel_id,
                is_user_sent=False,
                message_text=message_text,
            )
        elif bot_output.message_type == MessageType.IMAGE:
            channel_id = WhatsappHelper.wa_send_image(
                wa_bnumber=wa_bnumber,
                wa_api_key=wa_api_key,
                user_tele=user_identifier,
                message=message_text,
                header=bot_output.header,
                body=message_text,
                footer=bot_output.footer,
                menu_selector=bot_output.menu_selector,
                menu_title=bot_output.menu_title,
                options=(
                    [option.model_dump() for option in bot_output.options_list]
                    if bot_output.options_list
                    else None
                ),
                media_url=bot_output.message_data.media_url,
            )

            await create_message(
                turn_id=message.turn_id,
                message_type="image",
                channel="WA",
                channel_id=channel_id,
                is_user_sent=False,
                message_text=message_text,
            )
        elif bot_output.message_type == MessageType.DOCUMENT:
            channel_id = WhatsappHelper.wa_send_document(
                wa_bnumber=wa_bnumber,
                wa_api_key=wa_api_key,
                user_tele=user_identifier,
                document_url=bot_output.message_data.media_url,
                document_name=bot_output.message_data.message_text,
            )
            await create_message(
                turn_id=message.turn_id,
                message_type="document",
                channel="WA",
                channel_id=channel_id,
                is_user_sent=False,
                message_text="",
                media_url=bot_output.message_data.media_url,
            )
        elif bot_output.message_type == MessageType.FORM:
            channel_id = WhatsappHelper.wa_send_form(
                wa_bnumber=wa_bnumber,
                wa_api_key=wa_api_key,
                user_tele=user_identifier,
                flow_id=bot_output.wa_flow_id,
                screen_id=bot_output.wa_screen_id,
                body=bot_output.message_data.message_text,
                footer=bot_output.footer,
                token=bot_output.form_token,
            )
            await create_message(
                turn_id=message.turn_id,
                message_type="form",
                channel="WA",
                channel_id=channel_id,
                is_user_sent=False,
                message_text=bot_output.message_data.message_text,
            )
    logger.info("Message sent")
