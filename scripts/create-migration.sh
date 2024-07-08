#!/bin/bash

msg=$1

if ! python3 -c 'import sys; assert sys.version_info >= (3, 11)' 2>/dev/null; then
    echo "Please use python3.11 or newer"
    exit 1
fi


python3 -m venv .venv
source .venv/bin/activate
pip3 install alembic psycopg2-binary
pip3 install -e ./jb-lib/

# source ./set_jbhost.sh

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


set -a
source .env-dev
set +a

alembic revision --autogenerate -m "$msg"
