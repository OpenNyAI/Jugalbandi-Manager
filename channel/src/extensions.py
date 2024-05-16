import os
import logging
from dotenv import load_dotenv
from lib.kafka_utils import KafkaConsumer, KafkaProducer
from lib.azure_storage import AzureStorage

load_dotenv()
logging.basicConfig()
logger = logging.getLogger("channel")
logger.setLevel(logging.INFO)

azure_creds = {
    "account_url": os.getenv("STORAGE_ACCOUNT_URL"),
    "account_key": os.getenv("STORAGE_ACCOUNT_KEY"),
    "container_name": os.getenv("STORAGE_AUDIOFILES_CONTAINER"),
    "base_path": "input/",
}
storage = AzureStorage(**azure_creds)

channel_topic = os.getenv("KAFKA_CHANNEL_TOPIC")
language_topic = os.getenv("KAFKA_LANGUAGE_TOPIC")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")

logger.info("Connecting to kafka topic: %s", channel_topic)
consumer = KafkaConsumer.from_env_vars(
    group_id="cooler_group_id", auto_offset_reset="latest"
)
logger.info("Connected to kafka topic: %s", channel_topic)

logger.info("Connecting to kafka topic: %s", language_topic)
producer = KafkaProducer.from_env_vars()
logger.info("Connected to kafka topic: %s %s", language_topic, flow_topic)
