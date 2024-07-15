"""Main module for language service."""

import asyncio
import json
import os
import logging
import traceback
from typing import List, Callable
from dotenv import load_dotenv

from .crud import (
    get_turn_information,
    get_user_preferred_language,
)
from .handlers import handle_input, handle_output

from lib.data_models import (
    Channel,
    Flow,
    Language,
    LanguageIntent,
)
from lib.kafka_utils import KafkaConsumer, KafkaProducer
from lib.model import LanguageCodes

load_dotenv()

logger = logging.getLogger("language")
logger.setLevel(logging.INFO)

kafka_broker = os.getenv("KAFKA_BROKER")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")
language_topic = os.getenv("KAFKA_LANGUAGE_TOPIC")
channel_topic = os.getenv("KAFKA_CHANNEL_TOPIC")

logger.info("Connecting with topic: %s", language_topic)

consumer = KafkaConsumer.from_env_vars(
    group_id="cooler_group_id", auto_offset_reset="latest"
)
producer = KafkaProducer.from_env_vars()

logger.info("Connected with topic: %s", language_topic)


def send_message(data: Flow | Channel):
    """Sends message to Kafka topic"""
    topic = flow_topic if isinstance(data, Flow) else channel_topic
    msg = data.model_dump_json()
    logger.info("Sending message to %s topic: %s", topic, msg)
    producer.send_message(topic, msg)


async def handle_incoming_message(language_input: Language, callback: Callable):
    """Handler for Language Input"""
    turn_id = language_input.turn_id
    message_intent = language_input.intent

    preferred_language_code = await get_user_preferred_language(turn_id)
    if preferred_language_code is None:
        preferred_language = LanguageCodes.EN
    else:
        preferred_language = LanguageCodes.__members__.get(
            preferred_language_code.upper(), LanguageCodes.EN
        )
    logger.info("User Preferred Language: %s", preferred_language)

    if message_intent == LanguageIntent.LANGUAGE_IN:
        message = language_input.message
        flow_input = await handle_input(
            turn_id=turn_id,
            preferred_language=preferred_language,
            message=message,
        )
        callback(flow_input)

    elif message_intent == LanguageIntent.LANGUAGE_OUT:
        turn_id = language_input.turn_id
        message = language_input.message
        channel_inputs: List[Channel] = await handle_output(
            turn_id=turn_id, preferred_language=preferred_language, message=message
        )
        for channel_input in channel_inputs:
            callback(channel_input)


async def start():
    """Starts the language service."""
    while True:
        try:
            msg = consumer.receive_message(language_topic)
            logger.info("Received message %s", msg)
            msg = json.loads(msg)
            input_data = Language(**msg)
            logger.info("Received message %s", input_data)
            await handle_incoming_message(input_data, callback=send_message)
        except Exception as e:
            logger.error("Error %s :: %s", e, traceback.format_exc())


asyncio.run(start())
