# Azure CLI
az deployment group create --resource-group $RESOURCE_GROUP --template-file create_storage_template.json --parameters storageAccountName=testingjbstorage location=centralindia containerName=audiofiles

# Powershell
az deployment group create --resource-group $env:RESOURCE_GROUP --template-file create_storage_template.json --parameters storageAccountName=testingjbstorage location=centralindia containerName=audiofiles