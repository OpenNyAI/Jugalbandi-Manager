import logging
from .kafka_producer import KafkaProducer
from .kafka_consumer import KafkaConsumer

logger = logging.getLogger(__name__)

class KafkaHandler:
    __producer__ = None
    __consumer__ = None

    @classmethod
    def get_producer(cls) -> KafkaProducer:
        if cls.__producer__ is None:
            logger.info("Creating Kafka Producer")
            cls.__producer__ = KafkaProducer.from_env_vars()
        return cls.__producer__

    @classmethod
    def get_consumer(cls) -> KafkaConsumer:
        if cls.__consumer__ is None:
            group_id = "cooler_group_id"
            logger.info("Creating Kafka Consumer with group_id: %s", group_id)
            cls.__consumer__ = KafkaConsumer.from_env_vars(
                group_id=group_id, auto_offset_reset="latest"
            )
        return cls.__consumer__
