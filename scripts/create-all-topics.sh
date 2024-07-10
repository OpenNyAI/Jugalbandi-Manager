#!/bin/bash

kafka_ready() {
    kafka-topics.sh --bootstrap-server localhost:9092 --list > /dev/null 2>&1
}

# Wait for Kafka to be ready
while ! kafka_ready; do
    echo "Waiting for Kafka to be ready..."
    sleep 5
done

echo "Creating topics now"

kafka-topics.sh --create --bootstrap-server localhost:9092 --topic channel --if-not-exists
kafka-topics.sh --create --bootstrap-server localhost:9092 --topic language --if-not-exists
kafka-topics.sh --create --bootstrap-server localhost:9092 --topic flow --if-not-exists
kafka-topics.sh --create --bootstrap-server localhost:9092 --topic retriever --if-not-exists
kafka-topics.sh --create --bootstrap-server localhost:9092 --topic indexer --if-not-exists
