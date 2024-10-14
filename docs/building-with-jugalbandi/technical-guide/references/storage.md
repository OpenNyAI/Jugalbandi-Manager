---
layout: default
title: Storage
---

# Integrate Azure/Local Storage with Jugalbandi-Manager
***

JB Manager leverages [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) for the persistent storage of input and output files through which user interacts with the bot. Alternatively, we have the flexibility of switching to a local storage as well. 

In this document, we have covered the below-mentioned aspects for utilizing either of the storages effectively:
- Introduction
  - Preferred Scenario 
  - Prerequisites
- Step-by-step Configuration


## Introduction
### Azure Blob Storage
 - **Preferred Scenario**:
   - **Scalability Needs**: When you need to scale storage capacity quickly and efficiently without worrying about hardware limitations
   - **High Availability and Durability**: When you require high availability and durability with data redundancy across multiple locations
   - **Managed Services**: When you want to offload hardware maintenance, updates, and critical issue management to a cloud provider
 - **Prerequisites**:
   - **Azure Storage Account**: First, you will need to setup an Azure Storage Account on the portal (refer the [link](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal))
   - **Containers**: Next, you will create a container which will be used to store the files

### Local Storage
 - **Preferred Scenario**:
   - **High-Speed Access Required**: When applications require very low latency and high-speed access to data
   - **Complete Data Control**: When you need full control over data storage, management, and security (highly confidential files)
 - **Prerequisites**:
   - **Hardware Requirements**: Ensure you have sufficient hardware resources, such as hard drives (HDDs) or solid-state drives (SSDs), to meet your storage needs
   - **Backup and Redundancy**: Implement robust backup and redundancy strategies to protect against data loss due to hardware failures or other issues


## Configuration
### Setting up Environment Variables
 - To use **Azure Blob Storage**, you need to update the following lines in `.env-dev`:
   ```
      STORAGE_TYPE=azure
      AZURE_STORAGE_ACCOUNT_URL=<your_storage_account_url>
      AZURE_STORAGE_ACCOUNT_KEY=<your_storage_account_key>
      AZURE_STORAGE_CONTAINER=<your_container_name>
   ```
 - To use **Local Storage**, you need to update the following lines in `.env-dev`:
   ```
     STORAGE_TYPE=local
     PUBLIC_URL_PREFIX=<tunnerl_url>
   ```
 - By default, the JB Manager utilizes **Local Storage** unless specified using the above pointers
   
### FAQs:
 - What is the significance of `PUBLIC_URL_PREFIX`? 
   - To refer and access the inputted files across services in the JB Manager i.e. `Language` service in case of audio files
 
 - What are the default storage paths in both cases?
   - In case of Azure Blob Storage, default location is `/tmp/jb_files` within the defined container
   - While, in case of local storage, default location is `/mnt/jb_files`

 - I am already utilizing the `tmp` folder in the Azure Blob storage container in a different process. So is there a way to change the default path?
   - Yes, you could define the custom path in `azure_storage.py` at `jb-lib/lib/file_storage/azure` in case of Azure option
   ```
       class AzureAsyncStorage(AsyncStorage):
          __client__ = None
          tmp_folder = "/tmp/jb_files" # Update the path here
   ```
   - While in case of local storage, update the `local_storage.py` at `jb-lib/lib/file_storage/local/`
   ```
      class LocalAsyncStorage(AsyncStorage):
         tmp_folder = "/mnt/jb_files" # Update the path here
   ```