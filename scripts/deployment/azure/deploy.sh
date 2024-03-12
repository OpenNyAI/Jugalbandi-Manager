# defining & setting environment variables
export random_number=$RANDOM

# check if $rg_name is set to a value, if not set it to a default value
if [ -z "$rg_name" ]; then
    rg_name=rgjb-manager$random_number
fi

echo "Resource Group Name : $rg_name"

export RESOURCE_GROUP=$rg_name
export preferred_region=eastus2
export azureopenai_region=eastus2
export azurespeech_region=eastus2
export azuretranslation_region=eastus2
export azurespeech_key=
export azuretranslation_key=
export azureopenai_account=azureopenai-$random_number
export azurespeech_account=azurespeech-$random_number
export azuretranslation_account=azuretranslation-$random_number
export subscription_id=
export embeddings_model_name=ada-embeddings-$random_number
export gpt35_model_name=gpt35-$random_number
export gpt4_model_name=gpt4-$random_number
export storage_account_name=jbmanager$random_number
export storage_account_audiofiles_container_name=audiofiles
export container_app_environment_name=jb-managerenv-$random_number
export container_app_environment_workload_profile_name=envwp-$random_number


# check if variable directRun (if set to false or null, indicates this called by an Azure ARM Template) is set to true skip az login; else login to azure
echo "Direct Run: $directRun"
if [ "$directRun" = "true" ]; then
    echo "Direct Run"
else
    az login
fi

# get subscription id
subscription_id=$(az account show | jq -r .id)

# create resource group
az group create --name $rg_name --location $preferred_region

# create Speech, Translation & Azure OpenAI Resource
error_message=$(az cognitiveservices account create \
--name $azureopenai_account \
--resource-group $rg_name \
--location $azureopenai_region \
--kind OpenAI \
--sku S0 \
--custom-domain $azureopenai_account)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $error_message"
    exit 1
fi

# create Speech Resource
az cognitiveservices account create \
--name $azurespeech_account \
--resource-group $rg_name \
--location $azurespeech_region \
--kind SpeechServices \
--sku S0 \
--custom-domain $azurespeech_account

# create Translation Resource
az cognitiveservices account create \
--name $azuretranslation_account \
--resource-group $rg_name \
--location $azuretranslation_region \
--kind TextTranslation \
--sku S1 \
--custom-domain $azuretranslation_account


# get Speech, Translation & Azure OpenAI endpoint and keys
azureopenai_endpoint=$(az cognitiveservices account show \
--name $azureopenai_account \
--resource-group $rg_name \
| jq -r .properties.endpoint)

echo "Azure OpenAI Endpoint " $azureopenai_endpoint "\n"

azureopenai_key=$(az cognitiveservices account keys list \
--name $azureopenai_account \
--resource-group $rg_name \
| jq -r .key1)

echo "Azure OpenAI Key " $azureopenai_key "\n"

azuretranslation_key=$(az cognitiveservices account keys list \
--name $azuretranslation_account \
--resource-group $rg_name \
| jq -r .key1)

echo "Azure Translation Key " $azuretranslation_key "\n"

azurespeech_key=$(az cognitiveservices account keys list \
--name $azurespeech_account \
--resource-group $rg_name \
| jq -r .key1)

echo "Azure Speech Key " $azurespeech_key "\n"

# create text embeddings and GPT35 / GPT-4 deployments
error_message=$(az cognitiveservices account deployment create \
--name $azureopenai_account \
--resource-group  $rg_name \
--deployment-name $embeddings_model_name \
--model-name text-embedding-ada-002 \
--model-version 2 \
--model-format OpenAI)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $error_message"
    exit 1
fi

error_message=$(az cognitiveservices account deployment create \
--name $azureopenai_account \
--resource-group  $rg_name \
--deployment-name $gpt35_model_name \
--model-name gpt-35-turbo \
--model-version 0613 \
--model-format OpenAI)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $error_message"
    exit 1
fi

error_message=$(az cognitiveservices account deployment create \
--name $azureopenai_account \
--resource-group  $rg_name \
--deployment-name $gpt4_model_name \
--model-name gpt-4 \
--model-version 0613 \
--model-format OpenAI)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $error_message"
    exit 1
fi

# create ContainerApp Environment, Workload Profile and Container App
error_message=$(az containerapp env create \
-n $container_app_environment_name \
-g $rg_name \
--location $preferred_region \
--enable-workload-profiles)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $error_message"
    exit 1
fi

# error_message=$(az containerapp env workload-profile add \
# -g $rg_name \
# -n $container_app_environment_name \
# --workload-profile-name "Consumption" \
# --workload-profile-type D4 \
# --min-nodes 1 \
# --max-nodes 2)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $error_message"
    exit 1
fi

# source all common environment variables from jb-manager.env
source jb-manager.env

# set-up EventHub with KAFKA endpoint
# create standard eventhub namespace

export EVENTHUB_NAMESPACE=ehnsjb-manager$random_number
export EVENTHUB_SEND_POLICY=ehspjb-manager$random_number
export EVENTHUB_LISTEN_POLICY=ehlpjb-manager$random_number


az eventhubs namespace create --name $EVENTHUB_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--location $preferred_region \
--sku Standard \
--capacity 1 \
--enable-auto-inflate true \
--maximum-throughput-units 10 \
--enable-kafka true \
--zone-redundant false

# create a standard 4 eventhub / topic with 1 partition each

# API
# az eventhubs eventhub create --name $KAFKA_CONSUMER_TOPIC \
# --namespace-name $EVENTHUB_NAMESPACE \
# --resource-group $RESOURCE_GROUP \
# --retention-time 1 \
# --partition-count 1 \
# --enable-capture false \
# --cleanup-policy Delete \
# --status Active

# FLOW
az eventhubs eventhub create --name $KAFKA_PRODUCER_FLOW_TOPIC \
--namespace-name $EVENTHUB_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--retention-time 1 \
--partition-count 1 \
--enable-capture false \
--cleanup-policy Delete \
--status Active

# CHANNEL
az eventhubs eventhub create --name $KAFKA_CHANNEL_TOPIC \
--namespace-name $EVENTHUB_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--retention-time 1 \
--partition-count 1 \
--enable-capture false \
--cleanup-policy Delete \
--status Active

# LANGUAGE
az eventhubs eventhub create --name $KAFKA_LANGUAGE_TOPIC \
--namespace-name $EVENTHUB_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--retention-time 1 \
--partition-count 1 \
--enable-capture false \
--cleanup-policy Delete \
--status Active

# create a shared policy one each for send and listen
az eventhubs namespace authorization-rule create --name $EVENTHUB_SEND_POLICY \
--namespace-name $EVENTHUB_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--rights Send


az eventhubs namespace authorization-rule create --name $EVENTHUB_LISTEN_POLICY \
--namespace-name $EVENTHUB_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--rights Listen


# show the eventhub connection string for both send and listen
KAFKA_PRODUCER_PASSWORD=$(az eventhubs namespace authorization-rule keys list --name $EVENTHUB_SEND_POLICY \
--namespace-name $EVENTHUB_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--query "primaryConnectionString")

KAFKA_CONSUMER_PASSWORD=$(az eventhubs namespace authorization-rule keys list --name $EVENTHUB_LISTEN_POLICY \
--namespace-name $EVENTHUB_NAMESPACE \
--resource-group $RESOURCE_GROUP \
--query "primaryConnectionString")

# create a Azure PostgreSQL Flexible Server with 2 vCores
# create a database with name jb-manager
# show the connection string for the database

export POSTGRESQL_SERVER_NAME=pgserver$random_number
export POSTGRESQL_SERVER_LOCATION=$preferred_region
export POSTGRESQL_SERVER_ADMIN_USER=jbmanageradmin
export POSTGRESQL_SERVER_ADMIN_PASSWORD=$(openssl rand -base64 12)
export POSTGRESQL_SERVER_DATABASE_NAME=jb-manager

# this will be updated for Production set-up to be a part of a VNET
error_message=$(az postgres flexible-server create --name $POSTGRESQL_SERVER_NAME \
--location $POSTGRESQL_SERVER_LOCATION \
--resource-group $RESOURCE_GROUP \
--sku-name "Standard_D2ds_v4" \
--tier "GeneralPurpose" \
--public-access "Enabled" \
--high-availability "Disabled" \
--backup-retention 7 \
--admin-user $POSTGRESQL_SERVER_ADMIN_USER \
--admin-password $POSTGRESQL_SERVER_ADMIN_PASSWORD \
--database-name $POSTGRESQL_SERVER_DATABASE_NAME)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "PostgreSQL Creation Error: $error_message"
    exit 1
fi

# show connection string
az postgres flexible-server show --name $POSTGRESQL_SERVER_NAME --resource-group $RESOURCE_GROUP --query "fullyQualifiedDomainName"
echo "Admin Username & Password - " $POSTGRESQL_SERVER_ADMIN_USER " : " $POSTGRESQL_SERVER_ADMIN_PASSWORD

# Create Storage Account and Container to store files uploaded
az storage account create \
--name $storage_account_name \
--resource-group $rg_name \
--location $preferred_region \
--sku Standard_LRS \
--allow-blob-public-access true

az storage container create \
--name $storage_account_audiofiles_container_name \
--account-name $storage_account_name \
--public-access blob

STORAGE_ACCOUNT_KEY=$(az storage account keys list \
--account-name $storage_account_name \
--resource-group $rg_name \
--query "[0].value")

export STORAGE_ACCOUNT_URL=https://$storage_account_name.blob.core.windows.net
export STORAGE_AUDIOFILES_CONTAINER=$storage_account_audiofiles_container_name

# setting Container App Environment Variables
export AZURE_SPEECH_KEY=$azurespeech_key
export AZURE_SPEECH_REGION=$azurespeech_region
export AZURE_TRANSLATION_KEY=$azuretranslation_key
export AZURE_TRANSLATION_RESOURCE_LOCATION=$azuretranslation_region
export AZURE_OPENAI_ENDPOINT=$azureopenai_endpoint

export OPENAI_API_KEY=$OPENAI_API_KEY
export OPENAI_API_TYPE=azure
export OPENAI_EMBEDDINGS_DEPLOYMENT=$OPENAI_EMBEDDINGS_DEPLOYMENT

export KAFKA_BROKER=$EVENTHUB_NAMESPACE.servicebus.windows.net:9093
export KAFKA_PRODUCER_USERNAME='$ConnectionString'
export KAFKA_CONSUMER_USERNAME='$ConnectionString'
export KAFKA_RAG_TOPIC=rag
export KAFKA_USE_SASL=true

export POSTGRES_DATABASE_HOST=$POSTGRESQL_SERVER_NAME
export POSTGRES_DATABASE_NAME=$POSTGRESQL_SERVER_DATABASE_NAME
export POSTGRES_DATABASE_PASSWORD=$POSTGRESQL_SERVER_ADMIN_PASSWORD
export POSTGRES_DATABASE_PORT=5432
export POSTGRES_DATABASE_USERNAME=$POSTGRESQL_SERVER_ADMIN_USER

# environment variables for container apps
export container_registry_name=docker.io
export jb_manager_app=opennyaiin/jugalbandi-manager
export api_container_app_name=api
export channel_container_app_name=channel
export flow_container_app_name=flow
export indexer_container_app_name=indexer
export language_container_app_name=language
export retriever_container_app_name=retriever
export container_version=1.0.0
export container_target_port=8000

echo "Creating API Container App" "\n"

# create Container App
container_app_fqdn=$(az containerapp create \
--name $api_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$jb_manager_app:$api_container_app_name-$container_version \
--environment $container_app_environment_name \
--ingres external \
--target-port $container_target_port \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 2 \
--workload-profile-name "Consumption" \
--scale-rule-name http-rule \
--scale-rule-http-concurrency 50 \
--env-vars "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD" "KAFKA_CHANNEL_TOPIC=$KAFKA_CHANNEL_TOPIC" "KAFKA_FLOW_TOPIC=$KAFKA_FLOW_TOPIC" "STORAGE_ACCOUNT_URL=$STORAGE_ACCOUNT_URL" "STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY" "STORAGE_AUDIOFILES_CONTAINER=$STORAGE_AUDIOFILES_CONTAINER" "ENCRYPTION_KEY=$ENCRYPTION_KEY" "WA_API_HOST=$WA_API_HOST" \
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
--image $container_registry_name/$jb_manager_app:$language_container_app_name-$container_version \
--environment $container_app_environment_name \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 1 \
--workload-profile-name "Consumption" \
--env-vars "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD" "KAFKA_FLOW_TOPIC=$KAFKA_FLOW_TOPIC" "KAFKA_CHANNEL_TOPIC=$KAFKA_CHANNEL_TOPIC" "KAFKA_LANGUAGE_TOPIC=$KAFKA_LANGUAGE_TOPIC" "KAFKA_CONSUMER_USERNAME=$KAFKA_CONSUMER_USERNAME" "KAFKA_CONSUMER_PASSWORD=$KAFKA_CONSUMER_PASSWORD" "BHASHINI_USER_ID=$BHASHINI_USER_ID" "BHASHINI_API_KEY=$BHASHINI_API_KEY" "BHASHINI_PIPELINE_ID=$BHASHINI_PIPELINE_ID" "AZURE_SPEECH_KEY=$AZURE_SPEECH_KEY" "AZURE_SPEECH_REGION=$AZURE_SPEECH_REGION" "AZURE_TRANSLATION_KEY=$AZURE_TRANSLATION_KEY" "AZURE_TRANSLATION_RESOURCE_LOCATION=$AZURE_TRANSLATION_RESOURCE_LOCATION" "STORAGE_ACCOUNT_URL=$STORAGE_ACCOUNT_URL" "STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY" "STORAGE_AUDIOFILES_CONTAINER=$STORAGE_AUDIOFILES_CONTAINER")

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi

container_app_fqdn=$(az containerapp create \
--name $flow_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$jb_manager_app:$flow_container_app_name-$container_version \
--environment $container_app_environment_name \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 1 \
--workload-profile-name "Consumption" \
--env-vars "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD" "KAFKA_FLOW_TOPIC=$KAFKA_FLOW_TOPIC" "KAFKA_CHANNEL_TOPIC=$KAFKA_CHANNEL_TOPIC" "KAFKA_RAG_TOPIC=$KAFKA_RAG_TOPIC" "KAFKA_LANGUAGE_TOPIC=$KAFKA_LANGUAGE_TOPIC" "KAFKA_CONSUMER_USERNAME=$KAFKA_CONSUMER_USERNAME" "KAFKA_CONSUMER_PASSWORD=$KAFKA_CONSUMER_PASSWORD" "STORAGE_ACCOUNT_URL=$STORAGE_ACCOUNT_URL" "STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY" "STORAGE_AUDIOFILES_CONTAINER=$STORAGE_AUDIOFILES_CONTAINER" "ENCRYPTION_KEY=$ENCRYPTION_KEY")

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi

container_app_fqdn=$(az containerapp create \
--name $channel_container_app_name \
--resource-group $rg_name \
--image $container_registry_name/$jb_manager_app:$channel_container_app_name-$container_version \
--environment $container_app_environment_name \
--cpu 0.5 \
--memory 1Gi \
--min-replicas 1 \
--max-replicas 1 \
--workload-profile-name "Consumption" \
--env-vars "POSTGRES_DATABASE_NAME=$POSTGRES_DATABASE_NAME" "POSTGRES_DATABASE_USERNAME=$POSTGRES_DATABASE_USERNAME" "POSTGRES_DATABASE_PASSWORD=$POSTGRES_DATABASE_PASSWORD" "POSTGRES_DATABASE_HOST=$POSTGRES_DATABASE_HOST" "POSTGRES_DATABASE_PORT=$POSTGRES_DATABASE_PORT" "KAFKA_BROKER=$KAFKA_BROKER" "KAFKA_USE_SASL=$KAFKA_USE_SASL" "KAFKA_PRODUCER_USERNAME=$KAFKA_PRODUCER_USERNAME" "KAFKA_PRODUCER_PASSWORD=$KAFKA_PRODUCER_PASSWORD" "KAFKA_LANGUAGE_TOPIC=$KAFKA_LANGUAGE_TOPIC" "KAFKA_FLOW_TOPIC=$KAFKA_FLOW_TOPIC" "KAFKA_CHANNEL_TOPIC=$KAFKA_CHANNEL_TOPIC" "KAFKA_CONSUMER_USERNAME=$KAFKA_CONSUMER_USERNAME" "KAFKA_CONSUMER_PASSWORD=$KAFKA_CONSUMER_PASSWORD" "STORAGE_ACCOUNT_URL=$STORAGE_ACCOUNT_URL" "STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY" "STORAGE_AUDIOFILES_CONTAINER=$STORAGE_AUDIOFILES_CONTAINER" "ENCRYPTION_KEY=$ENCRYPTION_KEY" "WA_API_HOST=$WA_API_HOST")

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $container_app_fqdn"
    exit 1
fi

# Write output to the file
echo "Output File Path: $AZ_SCRIPTS_OUTPUT_PATH"
echo '{"result": {"API FQDN": '$container_app_fqdn'}}' > $AZ_SCRIPTS_OUTPUT_PATH
cat $AZ_SCRIPTS_OUTPUT_PATH
