# Azure CLI
az deployment group create --resource-group $RESOURCE_GROUP --template-file create_eventhubns_template.json --parameters eventHubNamespaceName=$EVENTHUB_NAMESPACE_NAME

# Powershell
az deployment group create --resource-group $env:RESOURCE_GROUP --template-file create_eventhubns_template.json --parameters eventHubNamespaceName=$EVENTHUB_NAMESPACE_NAME
