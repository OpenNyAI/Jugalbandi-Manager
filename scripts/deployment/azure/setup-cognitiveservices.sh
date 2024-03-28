#!/bin/bash

if [ $# -lt 3 ]; then
    echo "Usage: $0 resource_group Preferred_region Identifier"
    exit 1
fi

export RESOURCE_GROUP=$1
export PREFERRED_REGION=$2
export IDENTIFIER=$3

export azureopenai_region=$PREFERRED_REGION
export azurespeech_region=$PREFERRED_REGION
export azuretranslation_region=$PREFERRED_REGION
export azurespeech_key=
export azuretranslation_key=
export azureopenai_account=azureopenai-$IDENTIFIER
export azurespeech_account=azurespeech-$IDENTIFIER
export azuretranslation_account=azuretranslation-$IDENTIFIER
export embeddings_model_name=ada-embeddings-$IDENTIFIER
export gpt35_model_name=gpt35-$IDENTIFIER
export gpt4_model_name=gpt4-$IDENTIFIER

# create Speech, Translation & Azure OpenAI Resource
error_message=$(az cognitiveservices account create \
--name $azureopenai_account \
--resource-group $RESOURCE_GROUP \
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
--resource-group $RESOURCE_GROUP \
--location $azurespeech_region \
--kind SpeechServices \
--sku S0 \
--custom-domain $azurespeech_account

# create Translation Resource
az cognitiveservices account create \
--name $azuretranslation_account \
--resource-group $RESOURCE_GROUP \
--location $azuretranslation_region \
--kind TextTranslation \
--sku S1 \
--custom-domain $azuretranslation_account


# get Speech, Translation & Azure OpenAI endpoint and keys
azureopenai_endpoint=$(az cognitiveservices account show \
--name $azureopenai_account \
--resource-group $RESOURCE_GROUP \
| jq -r .properties.endpoint)

echo "Azure OpenAI Endpoint " $azureopenai_endpoint "\n"

azureopenai_key=$(az cognitiveservices account keys list \
--name $azureopenai_account \
--resource-group $RESOURCE_GROUP \
| jq -r .key1)

echo "Azure OpenAI Key " $azureopenai_key "\n"

azuretranslation_key=$(az cognitiveservices account keys list \
--name $azuretranslation_account \
--resource-group $RESOURCE_GROUP \
| jq -r .key1)

echo "Azure Translation Key " $azuretranslation_key "\n"

azurespeech_key=$(az cognitiveservices account keys list \
--name $azurespeech_account \
--resource-group $RESOURCE_GROUP \
| jq -r .key1)

echo "Azure Speech Key " $azurespeech_key "\n"

# create text embeddings and GPT35 / GPT-4 deployments
error_message=$(az cognitiveservices account deployment create \
--name $azureopenai_account \
--resource-group  $RESOURCE_GROUP \
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
--resource-group  $RESOURCE_GROUP \
--deployment-name $gpt35_model_name \
--model-name gpt-35-turbo \
--model-version 0613 \
--model-format OpenAI)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: $error_message"
    exit 1
fi

# error_message=$(az cognitiveservices account deployment create \
# --name $azureopenai_account \
# --resource-group  $RESOURCE_GROUP \
# --deployment-name $gpt4_model_name \
# --model-name gpt-4 \
# --model-version 0613 \
# --model-format OpenAI)

# # Check if the command was successful
# if [ $? -ne 0 ]; then
#     echo "Error: $error_message"
#     exit 1
# fi

export AZURE_SPEECH_KEY=$azurespeech_key
export AZURE_SPEECH_REGION=$azurespeech_region
export AZURE_TRANSLATION_KEY=$azuretranslation_key
export AZURE_TRANSLATION_RESOURCE_LOCATION=$azuretranslation_region
export AZURE_OPENAI_ENDPOINT=$azureopenai_endpoint
export OPENAI_API_KEY=$OPENAI_API_KEY
export OPENAI_API_TYPE=azure
export OPENAI_EMBEDDINGS_DEPLOYMENT=$OPENAI_EMBEDDINGS_DEPLOYMENT
