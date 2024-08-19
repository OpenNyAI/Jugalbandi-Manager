---
layout: default
title: Speech and Translation
---

### Bhasini Translation API
JB Manager depends on Bhasini translation and speech processing functionalites for processing messages (both text and audio) in Indic languages. To access Bhasini API, register at [Bhashini](https://bhashini.gov.in/ulca/user/register). Detailed steps on prerequisite is available on [Bhasini Onboarding Page](https://bhashini.gitbook.io/bhashini-apis/pre-requisites-and-onboarding). After registration, `USER_ID`, `API_KEY` and `PIPELINE_ID` will be required. You can find `PIPELINE_ID` [here](https://bhashini.gitbook.io/bhashini-apis/pipeline-search-call).

### Azure Speech and Translation API
JB Manager depends on Azure speech and translation API for processesing non-Indic languages as well as fallback to Bhasini API.
1. [Create a Speech resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices) in the Azure portal.
2. Create a Translation resource in the Azure portal.
2. Procure the Speech and Translation resource key and region. After your resource is deployed, select Go to resource to view and manage keys. For more information about Azure AI services resources, see [Get the keys for your resource](https://learn.microsoft.com/en-in/azure/ai-services/multi-service-resource?pivots=azportal#get-the-keys-for-your-resource).