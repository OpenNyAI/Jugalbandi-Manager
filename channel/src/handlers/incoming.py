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
from lib.channel_handler import channel_map
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
    channel = channel_map[bot_input.channel_name]
    jb_channel = await get_channel_by_turn_id(turn_id)

    message: Message = channel.to_message(
        turn_id=turn_id, channel=jb_channel, bot_input=bot_input
    )
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
