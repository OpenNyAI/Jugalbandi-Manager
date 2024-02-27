# expects required environment variables to be set in jbmanager.env file.
source jbmanager.env

export container_registry_name=jbacrtest.azurecr.io
export api_container_app_name=jb-manager-api
export channel_container_app_name=jb-manager-channel
export flow_container_app_name=jb-manager-flow
export indexer_container_app_name=jb-manager-indexer
export language_container_app_name=jb-manager-language
export retriever_container_app_name=jb-manager-retriever
export container_version=$1
export container_app_environment_name=managedEnvironment-jbtest-b0c0
export container_target_port=8000
export rg_name=jb-test

echo "Creating API Container App" "\n"

# create Container App
container_app_fqdn=$(az containerapp create \
--name $api_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$api_container_app_name:$container_version \
--environment $container_app_environment_name \
--ingres external \
--target-port $container_target_port \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 2 \
--scale-rule-name http-rule \
--scale-rule-http-concurrency 50 \
--env-vars "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD       " "KAFKA_CHANNEL_TOPIC=$KAFKA_CHANNEL_TOPIC" "STORAGE_ACCOUNT_URL=$STORAGE_ACCOUNT_URL" "STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY" "STORAGE_LAWFILES_CONTAINER=$STORAGE_LAWFILES_CONTAINER" "STORAGE_AUDIOFILES_CONTAINER=$STORAGE_AUDIOFILES_CONTAINER" "WA_API_HOST=$WA_API_HOST" "WABA_NUMBER=$WABA_NUMBER" "WA_API_KEY=$WA_API_KEY" \
--query properties.configuration.ingress.fqdn)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi

echo "Container App FQDN " + $container_app_fqdn

container_app_fqdn=$(az containerapp create \
--name $language_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$language_container_app_name:$container_version \
--environment $container_app_environment_name \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 1 \
--env-vars "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD" "KAFKA_FLOW_TOPIC=$KAFKA_FLOW_TOPIC" "KAFKA_CHANNEL_TOPIC=$KAFKA_CHANNEL_TOPIC" "KAFKA_LANGUAGE_TOPIC=$KAFKA_LANGUAGE_TOPIC" "KAFKA_CONSUMER_USERNAME=$KAFKA_CONSUMER_USERNAME" "KAFKA_CONSUMER_PASSWORD=$KAFKA_CONSUMER_PASSWORD" "CSC_API_HOST=$CSC_API_HOST" "OPENAI_API_KEY=$OPENAI_API_KEY" "OPENAI_API_TYPE=$OPENAI_API_TYPE" "BHASHINI_USER_ID=$BHASHINI_USER_ID " "BHASHINI_API_KEY=$BHASHINI_API_KEY" "BHASHINI_PIPELINE_ID=$BHASHINI_PIPELINE_ID" "AZURE_SPEECH_KEY=$AZURE_SPEECH_KEY" "AZURE_SPEECH_REGION=$AZURE_SPEECH_REGION" "AZURE_TRANSLATION_KEY=$AZURE_TRANSLATION_KEY" "AZURE_TRANSLATION_RESOURCE_LOCATION=$AZURE_TRANSLATION_RESOURCE_LOCATION" "STORAGE_ACCOUNT_URL=$STORAGE_ACCOUNT_URL" "STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY" "STORAGE_AUDIOFILES_CONTAINER=$STORAGE_AUDIOFILES_CONTAINER")

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi

container_app_fqdn=$(az containerapp create \
--name $flow_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$flow_container_app_name:$container_version \
--environment $container_app_environment_name \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 1 \
--env-vars "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD" "KAFKA_FLOW_TOPIC=$KAFKA_FLOW_TOPIC" "KAFKA_CHANNEL_TOPIC=$KAFKA_CHANNEL_TOPIC" "KAFKA_RAG_TOPIC=$KAFKA_RAG_TOPIC" "KAFKA_LANGUAGE_TOPIC=$KAFKA_LANGUAGE_TOPIC" "KAFKA_CONSUMER_USERNAME=$KAFKA_CONSUMER_USERNAME" "KAFKA_CONSUMER_PASSWORD=$KAFKA_CONSUMER_PASSWORD" "CSC_API_HOST=$CSC_API_HOST" "CSC_API_AES_KEY=$CSC_API_AES_KEY" "CSC_API_AES_IV=$CSC_API_AES_IV" "OPENAI_API_KEY=$OPENAI_API_KEY" "OPENAI_API_TYPE=$OPENAI_API_TYPE" "EAZYDRAFT_TOKEN=$EAZYDRAFT_TOKEN" "STORAGE_ACCOUNT_URL=$STORAGE_ACCOUNT_URL" "STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY" "STORAGE_LAWFILES_CONTAINER=$STORAGE_LAWFILES_CONTAINER" "STORAGE_AUDIOFILES_CONTAINER=$STORAGE_AUDIOFILES_CONTAINER")

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi

container_app_fqdn=$(az containerapp create \
--name $channel_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$channel_container_app_name:$container_version \
--environment $container_app_environment_name \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 1 \
--env-vars "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD " "KAFKA_LANGUAGE_TOPIC=$KAFKA_LANGUAGE_TOPIC" "KAFKA_FLOW_TOPIC=$KAFKA_FLOW_TOPIC" "KAFKA_CHANNEL_TOPIC=$KAFKA_CHANNEL_TOPIC" "KAFKA_CONSUMER_USERNAME=$KAFKA_CONSUMER_USERNAME" "KAFKA_CONSUMER_PASSWORD=$KAFKA_CONSUMER_PASSWORD" "STORAGE_ACCOUNT_URL=$STORAGE_ACCOUNT_URL" "STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY" "STORAGE_LAWFILES_CONTAINER=$STORAGE_LAWFILES_CONTAINER" "STORAGE_AUDIOFILES_CONTAINER=$STORAGE_AUDIOFILES_CONTAINER" "WA_API_HOST=$WA_API_HOST" "WABA_NUMBER=$WABA_NUMBER" "WA_API_KEY=$WA_API_KEY")

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi

container_app_fqdn=$(az containerapp create \
--name $indexer_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$indexer_container_app_name:$container_version \
--environment $container_app_environment_name \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 1 \
--env-vars "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_CONSUMER_TOPIC=indexer" "KAFKA_PRODUCER_FLOW_TOPIC=flow" "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "OPENAI_API_TYPE=non" "OPENAI_EMBEDDINGS_DEPLOYMENT=ahsj" "OPENAI_API_KEY=$OPENAI_API_KEY" "DOCUMENT_LOCAL_STORAGE_PATH=./data")

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi

container_app_fqdn=$(az containerapp create \
--name $retriever_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$retriever_container_app_name:$container_version \
--environment $container_app_environment_name \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 1 \
--env-vars "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_RAG_TOPIC=$KAFKA_RAG_TOPIC" "KAFKA_FLOW_TOPIC=$KAFKA_FLOW_TOPIC      " "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD" "KAFKA_CONSUMER_USERNAME=$KAFKA_CONSUMER_USERNAME" "KAFKA_CONSUMER_PASSWORD=$KAFKA_CONSUMER_PASSWORD" "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "OPENAI_API_TYPE=$OPENAI_API_TYPE" "AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT" "OPENAI_API_KEY=$OPENAI_API_KEY" "OPENAI_EMBEDDINGS_DEPLOYMENT=$OPENAI_EMBEDDINGS_DEPLOYMENT" "DOCUMENT_LOCAL_STORAGE_PATH=$DOCUMENT_LOCAL_STORAGE_PATH")

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi