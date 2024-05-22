#!/bin/bash

topic=$1

# Get the container ID for the service
CONTAINER_ID=$(./scripts/get-container-id.sh kafka)

# Check for error
if [ $? -ne 0 ]; then
    exit 1
fi

docker exec -i $CONTAINER_ID kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic $topic








