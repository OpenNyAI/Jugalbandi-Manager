#!/bin/bash

topic=$1
message=$2

docker exec -i jb-manager-kafka-1 kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic $topic
