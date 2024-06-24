import json
from kafka import KafkaProducer
import os
import json

json.dumps()


folderName = "~/kafkaCerts/kafka-pizza/"
producer = KafkaProducer(
    bootstrap_servers="<INSTANCE_NAME>-<PROJECT_NAME>.aivencloud.com:<PORT>",
<<<<<<< HEAD
    security_protocol="SSL",
    ssl_cafile=folderName+"ca.pem",
    ssl_certfile=folderName+"service.cert",
    ssl_keyfile=folderName+"service.key",
    value_serializer=lambda v: json.dumps(v).encode('ascii'),
    key_serializer=lambda v: json.dumps(v).encode('ascii')

=======
    value_serializer=lambda v: json.dumps(v).encode('ascii'),
    key_serializer=lambda v: json.dumps(v).encode('ascii')
>>>>>>> f2019284dec84b241f954953ff6054da16df8439
)

producer.send("test-topic",
        key={"key": 1},
        value={"message": "hello world"}
    )
producer.flush()