# defining & setting environment variables
export random_number=$RANDOM

# check if $rg_name is set to a value, if not set it to a default value
if [ -z "$rg_name" ]; then
    rg_name=rgjb-manager$random_number
fi

echo "Resource Group Name : $rg_name"

export RESOURCE_GROUP=$rg_name
export preferred_region=eastus

export subscription_id=

# check if variable directRun (if set to false or null, indicates this called by an Azure ARM Template) is set to true skip az login; else login to azure
echo "Direct Run: $directRun"
if [ "$directRun" = "true" ]; then
    echo "Direct Run"
else
    if [ $# -lt 1 ]; then
        echo "Please provide the subscription id to proceed."
        exit 1
    fi
    subscription_id=$1
    az login -o none
    az account set --subscription "$subscription_id"
fi

# get subscription id
subscription_id=$(az account show | jq -r .id)

# create resource group
az group create --name $rg_name --location $preferred_region

# source all common environment variables from jb-manager.env
set -a
source jb-manager.env
set +a

DEPLOY_SCRIPT_PATH=$(dirname "$(readlink -f "$0" || realpath "$0")")
AZ_SCRIPTS_OUTPUT_PATH=$DEPLOY_SCRIPT_PATH/get-api-url.json

source $DEPLOY_SCRIPT_PATH/setup-cognitiveservices.sh "$rg_name" "$preferred_region" "$random_number"
source $DEPLOY_SCRIPT_PATH/setup-kafka.sh "$rg_name" "$preferred_region" "$random_number"
source $DEPLOY_SCRIPT_PATH/setup-postgres.sh "$rg_name" "$preferred_region" "$random_number"
source $DEPLOY_SCRIPT_PATH/setup-storage.sh "$rg_name" "$preferred_region" "$random_number"

source $DEPLOY_SCRIPT_PATH/deploy-containers.sh "$rg_name" "$preferred_region" "$random_number"