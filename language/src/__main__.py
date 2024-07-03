"""Main module for language service."""

import asyncio
import json
import os
import logging
import traceback
from typing import List
from dotenv import load_dotenv

from .crud import (
    get_turn_information,
    get_user_preferred_language,
)
from .handlers import handle_input, handle_output

from lib.data_models import (
    ChannelInput,
    FlowInput,
    LanguageInput,
    LanguageIntent,
)
from lib.kafka_utils import KafkaConsumer, KafkaProducer
from lib.model import Language

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


def send_message(data: FlowInput | ChannelInput):
    """Sends message to Kafka topic"""
    topic = flow_topic if isinstance(data, FlowInput) else channel_topic
    msg = data.model_dump_json()
    logger.info("Sending message to %s topic: %s", topic, msg)
    producer.send_message(topic, msg)


async def handle_incoming_message(
    language_input: LanguageInput, callback: callable = None
):
    """Handler for Language Input"""
    session_id = language_input.session_id
    message_intent = language_input.intent

    preferred_language_code = await get_user_preferred_language(session_id)
    if preferred_language_code is None:
        preferred_language = Language.EN
    else:
        preferred_language = Language.__members__.get(
            preferred_language_code.upper(), Language.EN
        )
    logger.info("User Preferred Language: %s", preferred_language)

    if message_intent == LanguageIntent.LANGUAGE_IN:
        flow_input = await handle_input(
            preferred_language=preferred_language,
            language_input=language_input,
        )
        callback(flow_input)

    elif message_intent == LanguageIntent.LANGUAGE_OUT:
        turn_id = language_input.turn_id
        turn_info = await get_turn_information(turn_id)
        channel_inputs: List[ChannelInput] = await handle_output(
            preferred_language=preferred_language,
            language_input=language_input,
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
            input_data = LanguageInput(**msg)
            logger.info("Received message %s", input_data)
            await handle_incoming_message(input_data, callback=send_message)
        except Exception as e:
            logger.error("Error %s :: %s", e, traceback.format_exc())


asyncio.run(start())
