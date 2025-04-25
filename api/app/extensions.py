import os
import logging
from lib.kafka_utils import KafkaProducer, KafkaException
from lib.data_models import Flow, Channel, Indexer, Logger

logger = logging.getLogger("jb-manager-api")

# Load Kafka topics from environment
channel_topic = os.getenv("KAFKA_CHANNEL_TOPIC")
if not channel_topic:
    raise ValueError("KAFKA_CHANNEL_TOPIC is not set in the environment")

flow_topic = os.getenv("KAFKA_FLOW_TOPIC")
if not flow_topic:
    raise ValueError("KAFKA_FLOW_TOPIC is not set in the environment")

indexer_topic = os.getenv("KAFKA_INDEXER_TOPIC")
if not indexer_topic:
    raise ValueError("KAFKA_INDEXER_TOPIC is not set in the environment")

logger_topic = os.getenv("KAFKA_LOGGER_TOPIC")
if not logger_topic:
    raise ValueError("KAFKA_LOGGER_TOPIC is not set in the environment")

logger.info("Channel Topic: %s", channel_topic)
logger.info("Flow Topic: %s", flow_topic)
logger.info("Indexer Topic: %s", indexer_topic)
logger.info("Logger Topic: %s", logger_topic)

# Kafka producer initialization
producer = KafkaProducer.from_env_vars()

# Map data model classes to their corresponding Kafka topics
TOPIC_MAP = {
    Flow: flow_topic,
    Channel: channel_topic,
    Indexer: indexer_topic,
    Logger: logger_topic,
}


def produce_message(message: Flow | Channel | Indexer | Logger) -> None:
    topic = TOPIC_MAP.get(type(message))

    if not topic:
        raise ValueError(f"Invalid message type: {type(message)}")

    try:
        logger.info("Sending msg to %s topic: %s", topic, message)
        producer.send_message(
            topic=topic,
            value=message.model_dump_json(exclude_none=True)
        )
    except KafkaException as e:
        logger.error("Failed to send message to Kafka topic %s: %s", topic, e)
        raise
