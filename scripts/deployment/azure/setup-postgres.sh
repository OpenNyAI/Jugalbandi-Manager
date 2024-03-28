#!/bin/bash

# create a Azure PostgreSQL Flexible Server with 2 vCores
# create a database with name jb-manager
# show the connection string for the database

if [ $# -lt 3 ]; then
    echo "Usage: $0 resource_group Preferred_region Identifier"
    exit 1
fi

export RESOURCE_GROUP=$1
export PREFERRED_REGION=$2
export IDENTIFIER=$3

export POSTGRESQL_SERVER_NAME=pgserver$IDENTIFIER
export POSTGRESQL_SERVER_LOCATION=$PREFERRED_REGION
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

export POSTGRES_DATABASE_HOST=$POSTGRESQL_SERVER_NAME
export POSTGRES_DATABASE_NAME=$POSTGRESQL_SERVER_DATABASE_NAME
export POSTGRES_DATABASE_PASSWORD=$POSTGRESQL_SERVER_ADMIN_PASSWORD
export POSTGRES_DATABASE_USERNAME=$POSTGRESQL_SERVER_ADMIN_USER