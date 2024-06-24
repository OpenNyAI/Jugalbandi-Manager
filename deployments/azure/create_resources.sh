# Powershell
# $env:RESOURCE_GROUP = "testResourceGroup"
# $env:LOCATION = "Central India"
# az group create --name $env:RESOURCE_GROUP --location $env:LOCATION

az deployment group create --resource-group $env:RESOURCE_GROUP --template-file create_resources_template.json --parameters namespaces_ehnstesting_name=ehnsamtst location=centralindia postgresqlServerName=pgsvramtst adminUser=jbadmin adminPassword=jbadmin123 databaseName=dbamtst storageAccountName=storageaccountamtst containerName=containeramtst containerAppEnvironmentName=managedenvamtst containerAppName=api containerTargetPort=8000 cpu="0.5" memory="1Gi" minReplicas=1 maxReplicas=2 environmentVariables='[{"name": "POSTGRES_DATABASE_NAME", "value": "your_db_name"},{"name": "POSTGRES_DATABASE_USERNAME", "value": "your_db_username"}]'