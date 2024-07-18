import base64
import logging
from lib.data_models import (
    RestBotInput,
    Flow,
    FlowIntent,
    UserInput,
    Dialog,
    Message,
    MessageType,
    Language,
    LanguageIntent,
    AudioMessage,
)
from lib.channel_handler import channel_map, ChannelHandler
from lib.file_storage import StorageHandler
from ..crud import get_channel_by_turn_id

logging.basicConfig()
logger = logging.getLogger("channel")
logger.setLevel(logging.INFO)


async def process_incoming_messages(turn_id: str, bot_input: RestBotInput):
    """Process incoming messages"""
    channel = channel_map[bot_input.channel_name]
    print(channel.get_audio)
    print(ChannelHandler.get_audio)
    jb_channel = await get_channel_by_turn_id(turn_id)

    message_type = channel.get_message_type(bot_input)
    logger.info("Message type: %s", message_type)

    if message_type == MessageType.TEXT:
        text_message = channel.to_text_message(bot_input)
        message = Message(
            message_type=MessageType.TEXT,
            text=text_message,
        )
    elif message_type == MessageType.AUDIO:
        encoded_audio_content = channel.get_audio(jb_channel, bot_input)
        audio_content = base64.b64decode(encoded_audio_content)
        audio_file_name = f"{turn_id}.ogg"
        storage = StorageHandler.get_async_instance()
        await storage.write_file(audio_file_name, audio_content, "audio/ogg")
        storage_url = await storage.public_url(audio_file_name)
        audio_message = AudioMessage(
            media_url=storage_url,
        )
        message = Message(
            message_type=MessageType.AUDIO,
            audio=audio_message,
        )
    elif message_type == MessageType.INTERACTIVE_REPLY:
        interactive_reply_message = channel.to_interactive_reply_message(bot_input)
        message = Message(
            message_type=MessageType.INTERACTIVE_REPLY,
            interactive_reply=interactive_reply_message,
        )
    elif message_type == MessageType.FORM_REPLY:
        form_reply_message = channel.to_form_reply_message(bot_input)
        message = Message(
            message_type=MessageType.FORM_REPLY,
            form_reply=form_reply_message,
        )
    elif message_type == MessageType.DIALOG:
        dialog_message = channel.to_dialog_message(bot_input)
        message = Message(
            message_type=MessageType.DIALOG,
            dialog=dialog_message,
        )
    else:
        return NotImplemented

    logger.info("Got a message: %s", message)
    if message:
        message_type = message.message_type
        if message_type == MessageType.TEXT or message_type == MessageType.AUDIO:
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
