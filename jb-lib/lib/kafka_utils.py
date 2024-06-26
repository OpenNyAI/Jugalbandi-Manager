from confluent_kafka import Producer, Consumer, KafkaException
import socket, os, logging


class KafkaProducer:    
    def __init__(self, bootstrap_servers: str, 
                 client_id: str = socket.gethostname(),
                 use_sasl=False,
                 sasl_mechanism="PLAIN", 
                 sasl_username="", 
                 sasl_password="", 
                 producer_config: dict ={}  # can be used to override previous configs
                 ):
        self.bootstrap_servers = bootstrap_servers
        if use_sasl:
            self.producer_config = {
                'bootstrap.servers': self.bootstrap_servers,
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': sasl_mechanism,
                'sasl.username': sasl_username,
                'sasl.password': sasl_password,
                'client.id': client_id,
                ** producer_config
            }
        else:
            self.producer_config = {
                'bootstrap.servers': self.bootstrap_servers,
                'client.id': client_id,
                ** producer_config
            }
        self.producer = Producer(self.producer_config)
        

    @staticmethod
    def from_env_vars(client_id: str = socket.gethostname(),
                      producer_config: dict ={}  # can be used to override previous configs
                      ):
        '''
        Creates a KafkaProducer from environment variables.
        Uses the following environment variables:
        - KAFKA_BROKER: comma-separated list of kafka brokers
        - KAFKA_USE_SASL: whether to use SASL authentication (default: False)
        - KAFKA_PRODUCER_USERNAME: SASL username (default: "")
        - KAFKA_PRODUCER_PASSWORD: SASL password (default: "")
        You can further override these by providing arguments in the producer_config dict.
        '''
        kafka_broker = os.getenv('KAFKA_BROKER')
        use_sasl = os.getenv('KAFKA_USE_SASL')
        producer_username = os.getenv('KAFKA_PRODUCER_USERNAME')
        producer_password = os.getenv('KAFKA_PRODUCER_PASSWORD')

        if type(use_sasl) == str and use_sasl.lower() == 'true':
            return KafkaProducer(kafka_broker, 
                                 client_id, 
                                 use_sasl=True, 
                                 sasl_username=producer_username, 
                                 sasl_password=producer_password,
                                 producer_config=producer_config)
        else:
            return KafkaProducer(kafka_broker, client_id,  producer_config=producer_config)


    def send_message(self, topic: str, 
                     value: str,
                     key: str = None, 
                     callback_func = None):
        '''Sends a message to a topic (via `produce()`) and flushes.'''
        
        self.producer.produce(topic, value=value, key=key, callback=callback_func)
        self.producer.flush()
            

    def _send_message_async(self, topic: str, 
                     value: str,
                     key: str = None, 
                     callback_func = None):
        self.producer.produce(topic, value=value, key=key, callback=callback_func)
    
    def poll_for_callback(self, timeout=1.0):
        '''Polls for callback. To be used with `send_message_async`'''
        self.producer.poll(timeout=timeout)


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, 
                 group_id: str,
                 auto_offset_reset: str,
                 use_sasl=False,
                 sasl_mechanism="PLAIN", 
                 sasl_username="", 
                 sasl_password="", 
                 consumer_config: dict ={}  # can be used to override previous configs
                 ):
        self.bootstrap_servers = bootstrap_servers
        if use_sasl:
            self.consumer_config = {
                'bootstrap.servers': self.bootstrap_servers,
                'group.id': group_id,
                'auto.offset.reset': auto_offset_reset,
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': sasl_mechanism,
                'sasl.username': sasl_username,
                'sasl.password': sasl_password,
                ** consumer_config
            }
        else:
            self.consumer_config = {
                'bootstrap.servers': self.bootstrap_servers,
                'group.id': group_id,
                'auto.offset.reset': auto_offset_reset,
                ** consumer_config
            }
        self.consumer = Consumer(self.consumer_config)
        self.subscribed=False
        self.subscribed_topics = []

    @staticmethod
    def from_env_vars(group_id: str, auto_offset_reset: str):
        '''
        Creates a KafkaConsumer from environment variables.
        Uses the following environment variables:
        - KAFKA_BROKER: comma-separated list of kafka brokers
        - KAFKA_USE_SASL: whether to use SASL authentication (default: False)
        - KAFKA_CONSUMER_USERNAME: SASL username (default: "")
        - KAFKA_CONSUMER_PASSWORD: SASL password (default: "")
        You can further override these by providing arguments in the consumer_config dict.
        '''
        kafka_broker = os.getenv('KAFKA_BROKER')
        use_sasl = os.getenv('KAFKA_USE_SASL')
        consumer_username = os.getenv('KAFKA_CONSUMER_USERNAME')
        consumer_password = os.getenv('KAFKA_CONSUMER_PASSWORD')

        print("Consumer from env vars")
        
        if type(use_sasl) == str and use_sasl.lower() == 'true':
            return KafkaConsumer(kafka_broker, 
                                 group_id, 
                                 auto_offset_reset,
                                 use_sasl=True, 
                                 sasl_username=consumer_username, 
                                 sasl_password=consumer_password)
        else:
            return KafkaConsumer(kafka_broker, 
                                 group_id, 
                                 auto_offset_reset)

    def subscribe(self, topics: list):
        self.consumer.subscribe(topics)
        self.subscribed=True
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
            return(msg.value().decode('utf-8'))




class KafkaConnector:

    def __init__(self, bootstrap_servers, group_id, auto_offset_reset):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.producer = Producer({'bootstrap.servers': self.bootstrap_servers})
        self.consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': self.auto_offset_reset
        })
        
    def send_message(self, topic, message):
        self.producer.produce(topic, value=message)
        self.producer.flush()

    def receive_message(self, topic, callback):
        self.consumer.subscribe([topic])
        while True:
            msg = self.consumer.poll(timeout=1000)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            callback(msg.value().decode('utf-8'))
        self.consumer.close()        


# import os, json

# from dotenv import load_dotenv
# load_dotenv()

# if __name__ == '__main__':
#     kafka_bootstrap_servers = os.environ.get('KAFKA_BROKER')
#     kafka_topic = os.environ.get('KAFKA_TOPIC')

#     print("Start")
#     print("kafka_brokers", kafka_bootstrap_servers)
#     print("topic", kafka_topic)

#     print("Producing...")
#     kafka_producer = KafkaProducer(kafka_bootstrap_servers)
#     kafka_producer.send_message(kafka_topic, "Hello World")

#     print("Consuming...")
#     kafka_consumer = KafkaConsumer(kafka_bootstrap_servers, 'cooler_group_id', 'latest')
#     msg = kafka_consumer.receive_message(kafka_topic)
#     print(msg)
#     print(json.loads(msg))
#     print("Done")