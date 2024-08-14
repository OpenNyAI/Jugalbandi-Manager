# Tips and Best Practices / FAQs (Including best practices for creating a knowledge base)

1. How does Jugalbandi Manager work?

Jugalbandi manager is an AI-powered stack designed to process and respond to user queries by leveraging RAG over a predefined set of documents and data.It uses LLMs to generate accurate and contextually relevant answers. It is designed to be highly-customisable and can be configured to be interoperable with a wide range of services. &#x20;

2. What is a knowledge base?&#x20;

A knowledge base (KB) is a structured repository of information that can be queried and used to provide answers or insights. It serves as the primary source of data that the Jugalbandi Manager uses to generate responses to user queries.

3. How can Jugalbandi Manager benefit my organisation?

Jugalbandi enables any organisation to converse with users in their preferred channel, language and mode (text or voice based) of communication. It can streamline information retrieval, reduce the time spent on searching for answers, for just about any problem faced by an organisation or the stakeholders of their programs.

4. How to create a knowledge base?

While most LLMs can consume documents and catalogues without any modifications, as the information fed to them becomes larger and more complex, the accuracy and reliability of the answers generated may tend to falter. Organising the information before they’re presented to the AI models can help overcome their limitations as they scale.&#x20;

_**Some things to keep in mind while creating a KB:**_

A. Identify the scope and categories

Determine the scope and main categories for the knowledge base. For example, for legal information, categories might include "Arbitration," "Contracts," "Dispute Resolution," etc. Setting a scope with appropriate version controls for each phase of development of an AI service allows for the testing of the generated answers to be more comprehensive. Organising the dataset by categories can help the team building the service and the LLMs differentiate between the datasets, and trace the origin of faulty answers.

B. Structure the data

&#x20;Use structured formats like CSV or Excel or JSONs/XMLl to store the data. Ensure each entry is clearly labelled with metadata such as titles, authors, dates, and keywords. Providing variations of questions that may be asked by different types of users can help the LLMs relate the questions to the appropriate answer.\
\
One example of this format is as follows:

| FAQ\_ID | QUESTION V1 | QUESTION V2 | QUESTION V3 | ANSWERS | LAW NAME 1 | LAW NAME 2 | LAW NAME 3 |
| ------- | ----------- | ----------- | ----------- | ------- | ---------- | ---------- | ---------- |

C. Create Cross-References:

Link related documents or sections to each other through cross-references, similar to hyperlinks on a website, to guide users and AI models through related content.\


D. Create embeddings:&#x20;

Use pre-trained models to generate embeddings for documents or sections. Embeddings are numerical representations of the data that capture semantic meaning, enhancing information retrieval. (Jugalbandi currently uses the model ‘text-embedding-ada-002’ and defaults to OpenAIEmbeddings) These embeddings are stored in a vector database (which are optimised for quick similarity searches) but can also be stored in a relational, noSQL databases or CSV/JSON/HDF5 files, although their performance may be relatively slower.

5. What are the limitations of using Jugalbandi Manager?

The accuracy of answers provided by Jugalbandi is dependent on the quality and comprehensiveness of the knowledge base it is built upon.\
Additionally, while the scope of AI is constantly widening, not every problem requires an AI solution. Each adopter needs to evaluate the necessity of using Jugalbandi, or any AI solution to their workstream, consider the costs of scaling a POC to serve their user base and alternative tech and non-tech interventions to address their problem.

6. Can Jugalbandi Manager be integrated with other systems?

Yes, Jugalbandi Manager can be integrated with various existing systems and platforms through APIs (and other integration tools such as webhooks, zapier, custom scripts and ETL tools), making it adaptable to the specific needs of different organisations.

8. What kind of support and training is available for adopters of Jugalbandi Manager?

Support and training are available in the documentation of Jugalbandi manager, replete with reference implementations, how-to guides and explanations of the stack and its operations. The OpenNyAI team is also available to facilitate teams to quickly adopt and start using the stack, and anyone can readily seek support through the discord channel.&#x20;
