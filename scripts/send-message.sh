#!/bin/bash

topic=$1
message=$2

echo $message | docker exec -i jb-manager-kafka-1 kafka-console-producer.sh --bootstrap-server localhost:9092 --topic $topic
echo "Sent message to $topic"
