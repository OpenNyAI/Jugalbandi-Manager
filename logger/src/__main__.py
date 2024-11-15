import asyncio
import json
import os
import logging
import traceback
from dotenv import load_dotenv
from .crud import create_api_logger, create_channel_logger, create_language_logger, create_flow_logger, create_retriever_logger
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
            logger.error(f"Message in Logger is: {msg}")
            service_name = msg.get("source")
            logger.error(f"Service name is: {service_name}")
            logger.info("Input received: %s", msg)
            input_data = Logger(**msg)
            logger.info(
                "Input received in object form: %s",
                input_data.model_dump(exclude_none=True),
            )

            if(service_name == "api"):
                logger.info("Coming from Api")
                await create_api_logger(user_id = input_data.logger_obj.user_id,
                                        turn_id = input_data.logger_obj.turn_id,
                                        session_id = input_data.logger_obj.session_id,
                                        status = input_data.logger_obj.status)
            elif(service_name == "channel"):
                logger.info("Coming from Channel")
                await create_channel_logger(
                    id = input_data.logger_obj.id,
                    turn_id=input_data.logger_obj.turn_id, 
                    channel_id=input_data.logger_obj.channel_id, 
                    channel_name=input_data.logger_obj.channel_name, 
                    msg_intent = input_data.logger_obj.msg_intent,
                    msg_type=input_data.logger_obj.msg_type, 
                    sent_to_service = input_data.logger_obj.sent_to_service,
                    status = input_data.logger_obj.status
                )
            elif(service_name == "language"):
                logger.info("Coming from Language")
                await create_language_logger(
                    id = input_data.logger_obj.id,
                    turn_id=input_data.logger_obj.turn_id, 
                    msg_id=input_data.logger_obj.msg_id, 
                    msg_state=input_data.logger_obj.msg_state, 
                    msg_language = input_data.logger_obj.msg_language,
                    msg_type = input_data.logger_obj.msg_type,
                    translated_to_language = input_data.logger_obj.translated_to_language,
                    translation_type = input_data.logger_obj.translation_type,
                    translation_model = input_data.logger_obj.translation_model,
                    response_time = input_data.logger_obj.response_time,
                    status = input_data.logger_obj.status
                )
            elif(service_name == "flow"):
                logger.info("Coming from Flow")
                await create_flow_logger(
                    id = input_data.logger_obj.id,
                    turn_id = input_data.logger_obj.turn_id,
                    session_id = input_data.logger_obj.session_id,
                    msg_id = input_data.logger_obj.msg_id,
                    msg_intent = input_data.logger_obj.msg_intent,
                    flow_intent = input_data.logger_obj.flow_intent,
                    sent_to_service = input_data.logger_obj.sent_to_service,
                    status = input_data.logger_obj.status
                )
            elif(service_name == "retriever"):
                logger.info("Coming from Retriever")
                await create_retriever_logger(
                    id = input_data.logger_obj.id,
                    turn_id = input_data.logger_obj.turn_id,
                    msg_id = input_data.logger_obj.msg_id,
                    retriever_type = input_data.logger_obj.retriever_type,
                    collection_name = input_data.logger_obj.collection_name,
                    top_chunk_k_value = input_data.logger_obj.top_chunk_k_value,
                    number_of_chunks = input_data.logger_obj.number_of_chunks,
                    chunks = input_data.logger_obj.chunks,
                    query = input_data.logger_obj.query,
                    status = input_data.logger_obj.status
                )
            else:
                logger.info("Service name not found")
        except Exception as e:
            logger.error("Error %s", e)
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(start_logger())
