# Local Development / Writing your own bot

If the application to be built using Jugalbandi is a conversational bot, it’s 5-steps for the bot to go-live:&#x20;

1. Launch Jugalbandi Manager UI. Typically this would be in: http://localhost:4173/
2. Fill in some details like the name of the bot, version and the entire contents of the FSM file. Click on "Install new bot".
3. Provide required data to create your bot. This may include credentials to access LLMs (if applicable, as in the case of OpenAI services).&#x20;
4. If Whatsapp is the chosen channel of communication for the bot, enter the number of an active Whatsapp Business Account (WABA). Since the service is running on a local HTTP server, the callback url for the tunnelling service (such as ngrok) needs to be registered with the service provider.&#x20;
5. Activate the bot by clicking the play icon. Verify that the status of the bot has been changed to ‘active’.&#x20;
