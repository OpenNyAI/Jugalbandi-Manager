import os
from typing import Dict, Optional
from confluent_kafka import Consumer, KafkaException


class KafkaConsumer:
    __consumer__ = None

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        auto_offset_reset: str,
        use_sasl=False,
        sasl_mechanism="PLAIN",
        sasl_username="",
        sasl_password="",
        consumer_config: Optional[Dict] = None,  # can be used to override previous configs
    ):
        if consumer_config is None:
            consumer_config = {}
        self.bootstrap_servers = bootstrap_servers
        if use_sasl:
            self.consumer_config = {
                "bootstrap.servers": self.bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": auto_offset_reset,
                "security.protocol": "SASL_SSL",
                "sasl.mechanism": sasl_mechanism,
                "sasl.username": sasl_username,
                "sasl.password": sasl_password,
                **consumer_config,
            }
        else:
            self.consumer_config = {
                "bootstrap.servers": self.bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": auto_offset_reset,
                **consumer_config,
            }
        self.consumer = Consumer(self.consumer_config)
        self.subscribed = False
        self.subscribed_topics = []

    @classmethod
    def from_env_vars(cls, group_id: str, auto_offset_reset: str):
        """
        Creates a KafkaConsumer from environment variables.
        Uses the following environment variables:
        - KAFKA_BROKER: comma-separated list of kafka brokers
        - KAFKA_USE_SASL: whether to use SASL authentication (default: False)
        - KAFKA_CONSUMER_USERNAME: SASL username (default: "")
        - KAFKA_CONSUMER_PASSWORD: SASL password (default: "")
        You can further override these by providing arguments in the consumer_config dict.
        """
        kafka_broker = os.getenv("KAFKA_BROKER")
        use_sasl = os.getenv("KAFKA_USE_SASL")
        consumer_username = os.getenv("KAFKA_CONSUMER_USERNAME")
        consumer_password = os.getenv("KAFKA_CONSUMER_PASSWORD")
        if not kafka_broker:
            raise ValueError("KAFKA_BROKER environment variable not set")

        if isinstance(use_sasl, str) and use_sasl.lower() == "true":
            if not consumer_username or not consumer_password:
                raise ValueError(
                    "KAFKA_USE_SASL is set to True, but KAFKA_CONSUMER_USERNAME or KAFKA_CONSUMER_PASSWORD is not set"
                )
            cls.__consumer__ = KafkaConsumer(
                kafka_broker,
                group_id,
                auto_offset_reset,
                use_sasl=True,
                sasl_username=consumer_username,
                sasl_password=consumer_password,
            )
        else:
            return KafkaConsumer(kafka_broker, group_id, auto_offset_reset)

    def subscribe(self, topics: list):
        self.consumer.subscribe(topics)
        self.subscribed = True
        self.subscribed_topics = topics

    def receive_message(self, topic, timeout=60) -> str:
        if not self.subscribed:
            self.subscribe([topic])
        while True:
            msg = self.consumer.poll(timeout)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            return msg.value().decode("utf-8")
