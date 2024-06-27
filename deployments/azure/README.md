## Azure Deployment
**IMPORTANT**: The commands below are written for Azure CLI in a Linux environment. Please refer to the [Azure CLI documentation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) for installation instructions.



1. Create a parameters file in the same directory as the template file, `mainTemplate.parameters.json` The parameters file should have the following structure:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "resourceNamePrefix": {
            "value": "jb-test" 
        },
        "location": {
            "value": "centralindia"
        },
        "postgresAdminUser": {
            "value": "postgres"
        },
        "postgresAdminPassword": {
            "value": "postgres"
        },
        "postgresDatabaseName": {
            "value": "jb_db"
        },
        "cpu": {
            "value": "0.5"
        },
        "memory": {
            "value": "1Gi"
        },
        "minReplicas": {
            "value": 1
        },
        "maxReplicas": {
            "value": 2
        },
        "bhashniApiKey": {
            "value": "xxx"
        },
        "bhashniPipelineID": {
            "value": "xxx"
        },
        "bhashniUserID": {
            "value": "xxx"
        },
        "encryptionKey": {
            "value": "xxx"
        },
        "whatsappAPIHost": {
            "value": "https://example.com"
        },
        "whatsappAPIKey": {
            "value": "xxx"
        }
    }
}
```


2. Run the following command to create the template spec:

```bash
az ts create   --name jbspec   --version "1.0a"   --resource-group jugalbandi-test   --location "centralindia"   --template-file "./mainTemplate.json"
```

3. Run the following command to create the deployment:

```bash
id=$(az ts show --name jbspec --resource-group jugalbandi-test --version "1.0a" --query "id")
az deployment group create --resource-group jugalbandi-test --template-spec $id  --parameters @mainTemplate.parameters.json
```

