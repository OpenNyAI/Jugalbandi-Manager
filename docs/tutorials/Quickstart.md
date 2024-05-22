# Quickstart Guide

## Prerequisite 
1. Docker - Ensure that your system has docker engine installed and running. For installation, please refer to [docker engine installation instruction](https://docs.docker.com/engine/install/).
2. Docker Compose - Ensure docker compose is enabled along with docker engine. Please refer to [docker compose installation instruction](https://docs.docker.com/compose/install/).

## Dependencies
### Azure Blob Storage Account
JB Manager depends on [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) for the persistent storage of input and output audio files through which user interacts with the bot.

You can either use an existing Azure storage account or [create a new azure storage account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal). After procurement of a storage account, [create a new container](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-portal#create-a-container) in that storage account which will be used to store the audio files.  

### Bhasini Translation API
JB Manager depends on Bhasini translation and speech processing functionalites for processing messages (both text and audio) in Indic languages. To access Bhasini API, register at [Bhashini](https://bhashini.gov.in/ulca/user/register).

### Azure Speech and Translation API
JB Manager depends on Azure speech and translation API for processesing non-Indic languages as well as fallback to Bhasini API.
1. [Create a Speech resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices) in the Azure portal.
2. Create a Translation resource in the Azure portal.
2. Procure the Speech and Translation resource key and region. After your resource is deployed, select Go to resource to view and manage keys. For more information about Azure AI services resources, see [Get the keys for your resource](https://learn.microsoft.com/en-in/azure/ai-services/multi-service-resource?pivots=azportal#get-the-keys-for-your-resource).
### Pinnacle Whatsapp API
For conversation with Bot, currently JB Manager depends on whatsapp access provided by [Pinnacle](https://www.pinnacle.in/whatsapp-business-api).

## Running JB Manager
1. Clone and Change the directory to the project root.
2. Copy the contents of `.env-dev.template` file to `.env-dev` in the same directory.
```bash
$ cp .env-dev.template .env-dev
```
3. Enter the values of `BHASHINI_USER_ID`,`BHASHINI_API_KEY`,`BHASHINI_PIPELINE_ID`,`AZURE_SPEECH_KEY`,`AZURE_SPEECH_REGION`,`AZURE_TRANSLATION_KEY`,`AZURE_TRANSLATION_RESOURCE_LOCATION`,`STORAGE_ACCOUNT_URL`, `STORAGE_ACCOUNT_KEY`, `STORAGE_AUDIOFILES_CONTAINER`
`WA_API_HOST` procured from the prerequisite step.
4. Generate an Encryption key using the following command 
```bash
$ dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64
``` 
and add it to `ENCRYPTION_KEY` in `.env-dev` file. 

Note: Remember to enclose value of `ENCRYPTION_KEY` within single quotes.

5. Start the `kafka` and `postgres` container.
```bash
$ bash scripts/run.sh kafka postgres
```

6. Create the relevant postgres tables.
```bash
$ bash scripts/upgrade-db.sh
```

7. Create relevant kafka topics.
```bash
$ bash scripts/create-topic.sh channel
$ bash scripts/create-topic.sh flow
$ bash scripts/create-topic.sh language
```

8. Start JB Manager
```bash
$ bash scripts/run.sh --stage api channel language flow frontend
```

## Bot Installation and Go Live
