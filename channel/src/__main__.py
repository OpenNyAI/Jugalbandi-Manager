import asyncio
import json
import logging
import traceback
from lib.data_models import (
    ChannelInput,
    ChannelIntent,
)
from .extensions import consumer, channel_topic
from .handler import process_incoming_messages, send_message_to_user

logging.basicConfig()
logger = logging.getLogger("channel")
logger.setLevel(logging.INFO)



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
