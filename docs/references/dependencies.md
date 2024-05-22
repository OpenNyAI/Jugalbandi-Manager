---
layout: default
title: Dependencies
---

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
