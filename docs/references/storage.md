---
layout: default
title: Azure Storage
---

JB Manager depends on [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) for the persistent storage of input and output audio files through which user interacts with the bot.

You can either use an existing Azure storage account or [create a new azure storage account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal). After procurement of a storage account, [create a new container](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-portal#create-a-container) in that storage account which will be used to store the audio files.  