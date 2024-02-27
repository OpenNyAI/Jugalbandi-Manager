#!/bin/bash

# Check if running on WSL2
if grep -qi microsoft /proc/version && grep -q WSL2 /proc/version; then
    JBHOST=$(hostname -I | awk '{print $1}')
    export JB_KAFKA_BROKER=${JBHOST}:9092
    export JB_POSTGRES_DATABASE_HOST=${JBHOST}
    echo "Setting Kakfa & Postgres host by WSL2 IP: ${JBHOST}"
else
    export JB_KAFKA_BROKER=kafka:9092
    export JB_POSTGRES_DATABASE_HOST=postgres
    echo "Setting Kakfa & Postgres host by docker-compose service name: kafka, postgres"
fi
