import logging
from lib.data_models import Message
from lib.channel_handler import channel_map
from ..crud import (
    get_user_by_turn_id,
    get_channel_by_turn_id,
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
    channel_name: str = jb_channel.type
    channel_handler = channel_map[channel_name]
    channel_handler.send_message(channel=jb_channel, user=jb_user, message=message)
    logger.info("Message type: %s", message.message_type)
    await create_message(
        turn_id=turn_id,
        message_type=message.message_type.value,
        is_user_sent=False,
        message=getattr(message, message.message_type.value).model_dump_json(
            exclude_none=True
        ),
    )
    logger.info("Message sent")
