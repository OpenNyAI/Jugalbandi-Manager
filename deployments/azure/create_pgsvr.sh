# Azure CLI
az deployment group create --resource-group $RESOURCE_GROUP --template-file create_pgsvr_template.json --parameters postgresqlServerName=testingpgsvr location=centralindia adminUser=jbadmin adminPassword=jbadmin123 databaseName=testdb

# Powershell
az deployment group create --resource-group $env:RESOURCE_GROUP --template-file create_pgsvr_template.json --parameters postgresqlServerName=testingpgsvr location=centralindia adminUser=jbadmin adminPassword=jbadmin123 databaseName=testdb