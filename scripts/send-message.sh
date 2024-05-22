#!/bin/bash

topic=$1
message=$2

# Get the container ID for the service
CONTAINER_ID=$(./scripts/get-container-id.sh kafka)

# Check for error
if [ $? -ne 0 ]; then
    exit 1
fi

echo $message | docker exec -i $CONTAINER_ID kafka-console-producer.sh --bootstrap-server localhost:9092 --topic $topic
echo "Sent message to $topic"
