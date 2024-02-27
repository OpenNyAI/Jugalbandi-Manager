#!/bin/bash

topic=$1

docker exec -i jb-manager-kafka-1 kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic $topic








