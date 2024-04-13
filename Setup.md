## Steps

1. Rename the **.env-dev.template** file to **.env-dev**
2. Start the **docker daemon** by using docker-cli or Docker desktop or colima.
3. Run the application by running the following command from the root folder in the terminal or command prompt.
    ```
    For Linux/Unix systems:
        ./scripts/run.sh
    
    For Windows:
        sh ./scripts/run.sh
    ```
4. Once all the services mentioned in the **docker-compose.yml** file have started running, you can check the status of the services by running the `docker ps` command in another terminal.
5. The DB tables have to be populated in the running postgres service. It can be achieved by running the below command from the root folder.
    ```
    For Linux/Unix systems:
        ./scripts/upgrade-db.sh
    
    For Windows:
        sh ./scripts/upgrade-db.sh
    ```
6. Missing keys procurement:
    * ***Storage keys***: 
        1. In Azure, create a new service in storage accounts and copy the values of storage account name and key present in access keys tab. They will form the values for STORAGE_ACCOUNT_URL and STORAGE_ACCOUNT_KEY present in the .env-dev respectively.
        2. In the newly created same storage account, create a container with your preferred name. This name will form the value for STORAGE_AUDIOFILES_CONTAINER.
    * ***Language keys***:
        1. For Bhashini keys, register an account in [Bhashini website](https://bhashini.gov.in/ulca/user/register) and get the values for BHASHINI_USER_ID, BHASHINI_API_KEY and BHASHINI_PIPELINE_ID in .env-dev file.
        2. For Azure keys, create resources in translator and speech services and copy the copys for the values for AZURE_TRANSLATION_KEY, AZURE_TRANSLATION_RESOURCE_LOCATION, AZURE_SPEECH_KEY and AZURE_SPEECH_REGION present in the respective **keys and endpoint** console.
    * ***Whatsapp keys***:
        1. Contact the pinnacle services to get whatsapp keys for the values of WA_API_HOST, WABA_NUMBER and WA_API_KEY.
7. Frontend configuration:
    * Once the necessary keys are procured, go to this running [frontend link](http://0.0.0.0:4173/) and click on install new bot and provide the required data to create your bot. The detailed information about the fields are given below:
        1. **Name [Mandatory]** is the name of the bot
        2. **DSL [Optional]** is the domain specific language code for fsm.py
        3. **Code [Mandatory]** is the fsm.py file python code
        4. **Requirements  [Optional if no specialised pacakge is used in code]** is the required packages name with their versions as we put them usually in requirements.txt or pyproject.toml dependencies
        5. **index_urls [Optional]** is for custom and private packages links to download them from (This is for the case you use a library that your team has developed and internally published)
        6. **version [Mandatory]** is the version of the bot
        7. **required_credentials [Mandatory]** These are the variable names present in the .env-dev file. Only the variable names should be present with comma separated between them.
    * Once the bot is created, click on the **settings (⚙) icon** to enter the given credentials values and click save to save the credentials values.
    * Then click on the **play (▶️) icon** to activate the bot by providing the whatsapp bot number and whatsapp api key.
    * Once the above steps are completed, the bot status will be changed from **inactive to active.**