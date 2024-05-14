import logging
import os
from lib.kafka_utils import KafkaProducer, KafkaException
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('jb-manager-api')

channel_topic = os.getenv("KAFKA_CHANNEL_TOPIC")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")
if not channel_topic or not flow_topic:
    raise Exception("Kafka topics not set")


# Connect Kafka Producer automatically using env variables
# and SASL, if applicable
producer = KafkaProducer.from_env_vars()

def produce_message(message: str, topic: str):
    try:
        logger.info("Sending msg to %s topic: %s", topic, message)  # With this line
        producer.send_message(topic=topic, value=message)
    except Exception as e:
        raise KafkaException(status_code=500, detail=f"Error producing message: {e}") from e