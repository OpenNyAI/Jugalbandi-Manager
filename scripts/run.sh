#!/bin/bash

# Default environment file
env_file=".env-dev"

# Process command-line arguments
while getopts 'e:' flag; do
  case "${flag}" in
    e) env_file="${OPTARG}" ;;
    *) echo "Usage: $0 [-e env_file] [service1 service2 ...]"
       exit 1 ;;
  esac
done

# Remove processed options from the arguments list
shift $((OPTIND -1))

# set -a
# source ./set_jbhost.sh
# set +a

if grep -qi microsoft /proc/version && grep -q WSL2 /proc/version; then
    JBHOST=$(hostname -I | awk '{print $1}')
    export JBHOST
    export JB_KAFKA_BROKER=${JBHOST}
    export JB_POSTGRES_DATABASE_HOST=${JBHOST}
    echo "Setting Kakfa & Postgres host by WSL2 IP: ${JBHOST}"
else
    export JBHOST=localhost
    export JB_KAFKA_BROKER=kafka:9092
    export JB_POSTGRES_DATABASE_HOST=postgres
    echo "Setting Kakfa & Postgres host by docker-compose service name: kafka, postgres"
fi

docker compose build $@

# Run docker-compose with the specified environment file and services
docker compose --env-file "$env_file" up $@
