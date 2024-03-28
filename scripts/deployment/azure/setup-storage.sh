#!/bin/bash

if [ $# -lt 3 ]; then
    echo "Usage: $0 resource_group Preferred_region Identifier"
    exit 1
fi

export RESOURCE_GROUP=$1
export PREFERRED_REGION=$2
export IDENTIFIER=$3

export storage_account_name=jbmanager$random_number
export storage_account_audiofiles_container_name=audiofiles

# Create Storage Account and Container to store files uploaded
az storage account create \
--name $storage_account_name \
--resource-group $RESOURCE_GROUP \
--location $PREFERRED_REGION \
--sku Standard_LRS

az storage container create \
--name $storage_account_audiofiles_container_name \
--account-name $storage_account_name \

STORAGE_ACCOUNT_KEY=$(az storage account keys list \
--account-name $storage_account_name \
--resource-group $RESOURCE_GROUP \
--query "[0].value")

export STORAGE_ACCOUNT_URL=https://$storage_account_name.blob.core.windows.net
export STORAGE_AUDIOFILES_CONTAINER=$storage_account_audiofiles_container_name
export STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY