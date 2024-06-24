import os
import socket
from typing import Dict, Optional
from confluent_kafka import Producer


class KafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str,
        client_id: str = socket.gethostname(),
        use_sasl=False,
        sasl_mechanism="PLAIN",
        sasl_username="",
        sasl_password="",
        producer_config: Optional[
            Dict
        ] = None,  # can be used to override previous configs
    ):
        if producer_config is None:
            producer_config = {}
        self.bootstrap_servers = bootstrap_servers
        if use_sasl:
            self.producer_config = {
                "bootstrap.servers": self.bootstrap_servers,
                "security.protocol": "SASL_SSL",
                "sasl.mechanism": sasl_mechanism,
                "sasl.username": sasl_username,
                "sasl.password": sasl_password,
                "client.id": client_id,
                **producer_config,
            }
        else:
            self.producer_config = {
                "bootstrap.servers": self.bootstrap_servers,
                "client.id": client_id,
                **producer_config,
            }
        self.producer = Producer(self.producer_config)

    @staticmethod
    def from_env_vars(
        client_id: str = socket.gethostname(),
        producer_config: Optional[
            Dict
        ] = None,  # can be used to override previous configs
    ):
        """
        Creates a KafkaProducer from environment variables.
        Uses the following environment variables:
        - KAFKA_BROKER: comma-separated list of kafka brokers
        - KAFKA_USE_SASL: whether to use SASL authentication (default: False)
        - KAFKA_PRODUCER_USERNAME: SASL username (default: "")
        - KAFKA_PRODUCER_PASSWORD: SASL password (default: "")
        You can further override these by providing arguments in the producer_config dict.
        """
        if producer_config is None:
            producer_config = {}
        kafka_broker = os.getenv("KAFKA_BROKER")
        use_sasl = os.getenv("KAFKA_USE_SASL")
        producer_username = os.getenv("KAFKA_PRODUCER_USERNAME")
        producer_password = os.getenv("KAFKA_PRODUCER_PASSWORD")
        if not kafka_broker:
            raise ValueError("KAFKA_BROKER environment variable not set")

        if isinstance(use_sasl, str) and use_sasl.lower() == "true":
            if not producer_username or not producer_password:
                raise ValueError(
                    "KAFKA_USE_SASL is set to True but KAFKA_PRODUCER_USERNAME and KAFKA_PRODUCER_PASSWORD are not set"
                )
            return KafkaProducer(
                kafka_broker,
                client_id,
                use_sasl=True,
                sasl_username=producer_username,
                sasl_password=producer_password,
                producer_config=producer_config,
            )
        else:
            return KafkaProducer(
                kafka_broker, client_id, producer_config=producer_config
            )

    def send_message(
        self, topic: str, value: str, key: Optional[str] = None, callback_func=None
    ):
        """Sends a message to a topic (via `produce()`) and flushes."""

        self.producer.produce(topic, value=value, key=key, callback=callback_func)
        self.producer.flush()

    def _send_message_async(
        self, topic: str, value: str, key: Optional[str] = None, callback_func=None
    ):
        self.producer.produce(topic, value=value, key=key, callback=callback_func)

    def poll_for_callback(self, timeout=1.0):
        """Polls for callback. To be used with `send_message_async`"""
        self.producer.poll(timeout=timeout)
