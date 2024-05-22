# Service name as defined in docker-compose.yml
SERVICE_NAME=$1

# Get the container ID for the service
CONTAINER_ID=$(docker-compose ps -q $SERVICE_NAME)

# Check if the container is running
if [ -z "$CONTAINER_ID" ]; then
    echo "No running container found for service: $SERVICE_NAME"
    exit 1
fi
echo $CONTAINER_ID