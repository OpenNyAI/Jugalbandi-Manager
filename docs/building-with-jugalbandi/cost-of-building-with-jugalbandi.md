# Cost of building with Jugalbandi

Accessing the Jugalbandi stack is and will remain free, through the project’s GitHub repository. To be able to utilise the stack to build and offer solutions, any individual or organisation needs to consider the cost of operating the application and the associated data & infrastructure.

The key considerations in budgeting for a conversational service is as follows:&#x20;

1. **Estimating the usage and plan to scale**&#x20;

* The amount of people using the service, how often they use it and the complexity of their queries will determine the associated costs of the cloud infrastructure and services that will be required for solutions such as Jugalbandi to operate
* For example, if 100 users send 30 messages each day, an estimated ₹656 per month would have to be budgeted for processing these messages using LLMs such as GPT-4o mini or 3.5.&#x20;
* Start small and add more resources as needed. This helps control costs and scale efficiently.
* Depending on the nature of the use case, cloud service providers are known to offer negotiated contracts to access their services at subsidised rates.&#x20;

2. **Monitoring data transfer and storage needs**

* Calculate how much data will need to be stored including user data, message logs and media files. This should also include the costs of encrypting and masking sensitive information.&#x20;
* The data in and out of cloud services, would have to be routinely monitored in accordance with the regional regulations on data protection and privacy.&#x20;

3. **Human Resources**

* Depending on the complexity of the use case, data scientists, data engineers and full stack developers may be needed to implement the solution as per the requirements.&#x20;

4. **Communication Costs**

* Based on the medium of communication with users, there may be additional costs incurred through third party service providers.&#x20;
* While the exact cost will vary based on the chosen service provider, at an estimated Rs. 0.3 per session, the same example from above of 100 users sending 30 messages a day would cost an additional \~Rs. 1000 a month over whatsapp.&#x20;

The following table indicates the costs associated with deploying and operating a platform with Jugalbandi manager: \


<table data-full-width="true"><thead><tr><th>Cost Category</th><th>Service Required</th><th>Indicative Cost (as of July 2024, and all costs are subject to the terms of the service provider)</th><th>Notes </th></tr></thead><tbody><tr><td><p><br><br></p><p>Cloud Infrastructure</p></td><td>Compute</td><td>~Rs. 10 per hour per VM</td><td>Running compute resources. The cost will vary based on usage</td></tr><tr><td>Storage</td><td>~Rs. 2 per GB</td><td>Storing user data and media. Estimated: ₹166.71 per month (assuming 100 GB)</td><td></td></tr><tr><td>Event Hubs for Kafka</td><td>~Rs. 120  per processing hour</td><td>Queue management for messaging between the various services of the platform.</td><td></td></tr><tr><td>Vector Databases</td><td>~Rs. 25 per hour</td><td>Scalable databases for AI models</td><td></td></tr><tr><td>Landing Zones</td><td>Can vary based on the chosen service providers</td><td>A one-time cost for the initial setup of cloud resources</td><td></td></tr><tr><td>Embedding Models</td><td>₹0.008336 to ₹0.010836 per 1000 tokens</td><td>Creating chunks of the provided knowledge bases to be consumed by AI models</td><td></td></tr><tr><td>Speech Processing</td><td>₹83.35 to ₹1,250.27 [per million characters or audio hours]</td><td>Converting speech to text, text to speech, and processing text.</td><td></td></tr><tr><td>LLMs</td><td>GPT-3.5 Turbo Tokens</td><td>₹0.125 (Input) + ₹0.167 (Output) per 1000 tokens</td><td>Processing user messages for AI responses. Estimated: ₹656 per month for a 100 users with 30 messages each</td></tr><tr><td>Technical implementation team: Data Scientists, Data Engineers &#x26; Full-Stack Devs</td><td></td><td></td><td></td></tr><tr><td>Whatsapp/Communication Channel Integration and Communication Services</td><td></td><td></td><td></td></tr><tr><td>Data handling, transfer, security and compliance costs</td><td></td><td></td><td></td></tr></tbody></table>

\
