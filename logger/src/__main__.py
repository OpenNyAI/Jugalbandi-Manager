import asyncio
import json
import os
import logging
import traceback
from dotenv import load_dotenv
from .crud import create_api_logger
from lib.data_models import (
    Logger,
)
from lib.kafka import KafkaHandler

load_dotenv()

logging.basicConfig()
logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)

channel_topic = os.getenv("KAFKA_CHANNEL_TOPIC")
if not channel_topic:
    raise ValueError("KAFKA_CHANNEL_TOPIC is not set in the environment")
language_topic = os.getenv("KAFKA_LANGUAGE_TOPIC")
if not language_topic:
    raise ValueError("KAFKA_LANGUAGE_TOPIC is not set in the environment")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")
if not flow_topic:
    raise ValueError("KAFKA_FLOW_TOPIC is not set in the environment")
logger_topic = os.getenv("KAFKA_LOGGER_TOPIC")
if not logger_topic:
    raise ValueError("KAFKA_LOGGER_TOPIC is not set in the environment")
logger.info("Channel Topic: %s", channel_topic)
logger.info("Language Topic: %s", language_topic)
logger.info("Flow Topic: %s", flow_topic)
logger.info("Logger Topic: %s", logger_topic)
consumer = KafkaHandler.get_consumer()
producer = KafkaHandler.get_producer()


async def start_logger():
    """Starts the logger server"""
    logger.info("Starting Listening")
    while True:
        try:
            msg = consumer.receive_message(logger_topic)
            msg = json.loads(msg)
            service_name = msg.get("source")
            logger.info("Input received: %s", msg)
            input_data = Logger(**msg)
            logger.info(
                "Input received in object form: %s",
                input_data.model_dump(exclude_none=True),
            )

            if(service_name == "api"):
                await create_api_logger(msg_id = input_data.api_logger.msg_id,
                                        user_id = input_data.api_logger.user_id,
                                        turn_id = input_data.api_logger.turn_id,
                                        session_id = input_data.api_logger.session_id,
                                        status = input_data.api_logger.status)
            elif(service_name == "Channel"):
                logger.info("Coming fron Channel")
            elif(service_name == "Flow"):
                logger.info("Coming from Flow")
            else:
                logger.info("Service name not found")
        except Exception as e:
            logger.error("Error %s", e)
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(start_logger())
