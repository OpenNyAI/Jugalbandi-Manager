# Jugalbandi for Govt. Schemes

**Community members involved**&#x20;

MySchemes, Digital India Corporation

**Problem statement**

Citizens often face difficulties in accessing relevant information about various government schemes due to the complexity of navigating through numerous central and state schemes. This makes it challenging for them to understand which schemes they qualify for and how to benefit from these government services.



**How the problem was addressed**

A service was developed that could accept open ended queries from users, understand their needs, and map these to the relevant government schemes. The service continuously asks follow-up questions until it has gathered enough information to provide accurate scheme recommendations. It can provide information about which scheme is most relevant for the user, benefits of the scheme, eligibility criteria, documents required.&#x20;



**What’s happening in the backend?**&#x20;

The jugalbandi [stack ](https://github.com/OpenNyAI/schemes\_chatbot\_deprecated)facilitated the following tasks:&#x20;

* Data Scraping: Extracting data from the MySchemes website to gather information about various government schemes.
* Data Structuring: Organising the scraped data into a predefined format for easy querying, which serves as the knowledge base for the service.&#x20;
* Intent classification: Handling user queries and prompt engineering to ensure comprehensive information retrieval.
* Integration with Bhashini Models: Uses Bhashini models for speech-to-text, translations, and text-to-speech functionalities.
* Feedback Loop: Continuously refining the system based on user interactions to improve accuracy.
* Answer Generation: Based on the highest ranked chunks from the provided knowledge base to provide the most relevant information to the user.&#x20;



<figure><img src="https://lh7-rt.googleusercontent.com/docsz/AD_4nXfYfwSuQ6mXE3xzQA_NB3Dfgu_38G7quxpKGRCKCCS1yoEnVYOXrz0Yvyim-jTrMi-3olk770F4Xl0OIDjAJvrto_Dakfx3_jJRwiWfbYhstAwpSTY8UWtfqUMa565wfvj4vzQhLK0WEjwT7HFIPgym5-Qx?key=BpTZdnbJWNo5iqrctUDI4Q" alt=""><figcaption></figcaption></figure>

_An illustration of Jugalbandi’s RAG pipeline_



**Implementation Requirements**

**Team:**&#x20;

2 Functional Personnel: To develop scripts, manage the knowledge base, oversee testing, and communicate with the developer.

**Timeline:**

Total 5 weeks including:&#x20;

Initial Setup and Data Scraping: 1 week

Data Manipulation and Organization: 1 week

Development of Query Handling and Follow-up Mechanisms: 1 week

Testing and Iteration: 1 week

Deployment and Monitoring: 1 week



**Roadblocks and Learnings**

Scalability: The initial versions were not highly scalable, but this has been improved with the Jugalbandi manager, which uses microservices and Kafka queues for better handling of multiple requests.

User Interaction: Designing the chatbot to ask the right follow-up questions was crucial for understanding user needs and providing accurate scheme recommendations.

\
\


###
