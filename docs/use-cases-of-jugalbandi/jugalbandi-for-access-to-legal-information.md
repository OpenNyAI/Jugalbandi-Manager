# Jugalbandi for Access to Legal Information

1. **Community members involved**

NHRC, Karnataka High Court, SEBI and the Department of Justice

2. **Problem statement**

The language of the law has often been inaccessible to the average citizen, regardless of the domain the law caters to. Interpreting the nuances of legal language and its linkages to related policies and other laws, has been the cornerstone of legal advice, which is almost never free. This complexity can reduce the law’s ability to protect its intended beneficiaries, hinder the ability of the agents of the state to enforce it and deter its effectiveness in curbing malpractices.

Even for institutions that serve, protect and enforce the law, their operations and administration can be eased with quicker access to legal research. The judicial system in India often faces prolonged case durations, taking an average of six to nine months to resolve a case. This lengthy process places a significant strain on judges, lawyers,litigants and the staff involved. A major contributing factor is the outdated and traditional methods of information retrieval used in the judiciary. Judges and court staff spend considerable time manually searching through legal documents and references, which delays the resolution process. For regulatory bodies, while detailed awareness and cautionary material have been publicly   released, their accessibility can still be improved. In the case of financial markets, SEBI’s investor awareness and support [portal](https://investor.sebi.gov.in/) sits on a wealth of such information. However, it doesn’t yet have the ability to be queried conversationally.&#x20;

Another avenue of the law where there’s a pressing need for credible legal information is in the case of India’s migration to the new criminal laws, wherein the three primary criminal laws of the country were replaced. The Bharatiya Nyaya Sanhita (BNS) replaces the Indian Penal Code (IPC), the Bharatiya Nagarik Suraksha Sanhita (BNSS) replaces the Criminal Procedure Code (CrPC), and the Bharatiya Sakshya Adhiniyam (BSA) replaces the Indian Evidence Act (IEA). With the new laws set to come in place on the 1st July 2024, a solution was sought that could allow agencies of the state (such as the police), lawyers etc. to quickly map their understanding of the old laws to the newer provisions, and quickly get up to speed with the changes in the newer laws.&#x20;

3. **How the problem was addressed**

Through the Jagrit telegram bots, Jugalbandi aimed to create a more accessible and user-friendly legal information system to deal with matters of motor vehicle accidents and domestic violence. The solution involved converting legal documents into a question-and-answer format, allowing users to ask specific legal questions and receive direct answers. Particularly in the case of domestic violence queries, Jagrit was designed to be sensitive to the nature of queries and to not store or process any information that could be used to identify the person seeking legal help.&#x20;

For such complex issues, users may also choose to be connected with legal advisors through services such as TeleLaw.in, within the regional language chat interface.

JIVA, short for Judges Intelligent Virtual Assistant, is a Jugalbandi-powered tool designed to aid judges in their search for laws and legal information. With just a few keywords or a specific query, JIVA enables judges to swiftly access and retrieve the relevant PDFs of legislation or specific sections. This advanced tool has been fine-tuned to cater to Karnataka-specific state laws and specific central laws. By focusing on these specific legal domains, JIVA ensures that judges in Karnataka have access to accurate and up-to-date information that is relevant to their jurisdiction, which could be queried via text or voice.&#x20;

Jugalbandi was configured to assist SEBI by extracting relevant information from regulatory filings and investor awareness documents. Users could then conversationally go through these documents or ask pointed questions that they may have in their dealings with securities & financial assets.&#x20;

An instance of Jugalbandi was created with the knowledge base that included a comparative study of the IPC, CrPC, IEA  & BNS, BNSS and BSA acts. This process involved preparing and cleaning an excel sheet that mapped the relevant sections and subsections of the older laws to the newer laws.This data was then structured into chunks, with each chunk containing relevant sections, titles, content, and consequences from both old and new laws. This structured data was used to create a repository of information that the bot could query.

4. **User Journey**

For the conversational bots, the user could use it in one of two ways:&#x20;

* Mention the section/sub-section of the relevant laws and get information about related acts or newer versions of the law
* Ask general queries about matters related to criminal law, and the application would provide the answers&#x20;
* In use cases where the Jugalbandi service were integrated with services such as the DoJ’s Nyaya Setu, the service could connect users to legal advisors registered on the platform, ensuring the users receive comprehensive assistance.

Some of these implementations also took the shape of a dashboard. The user could use said dashboard to:&#x20;

* Retrieve the appropriate legal document relating to a matter
* Retrieve the relevant section/sub-section of a legal document
* Avail the services of a chatbot, as with the previous example\


5\. **What’s happening in the backend?**

Prompts and Query Handling: Legal documents are converted into an FAQ format, ensuring complete and coherent chunks of information. Jugalbandi first processes the user's query, identifying sections and subsections if specified, after matching it to the relevant FAQs fed as knowledge bases while building the service.

Metadata Filtering: When a user submits a query, Jugalbandi extracts relevant metadata such as section numbers and titles.This metadata is then used to enhance the semantic search process, making it more precise. The metadata includes details like the source document, section numbers, titles, and any related subsections.\
An example of how this metadata has been organised for searching for titles or specific sections of a document has been indicated in the appendix.

Retrieval: Jugalbandi retrieves the top five relevant chunks from the knowledge base based on the query and metadata. These chunks contain the necessary information to answer the user's query.

Answer Generation using LLMs: The language model (typically GPT-4o mini or 3.5) processes the retrieved chunks to extract the most suitable and relevant answers, which are then presented to the user.

Accessing information from third party services: Where necessary, the Jugalbandi service can retrieve information from a trusted information and services provider. For example: contact details about lawyers who specialise in the types of cases relevant to the user’s grievance or disputes.&#x20;

6. **Implementation requirements Tools:**&#x20;

* API services to communicate with a whatsapp business account&#x20;
* Indexed legal datasets such as FAQ database for domestic violence and motor vehicle laws.

Team:&#x20;

* Developers to handle the technical development and maintenance
* Functional/product personnel to develop scripts, manage knowledge bases (with one spreadsheet mapping the changes from the old laws to the new for each of the three criminal laws), oversee testing, and maintain communication with the developer.

7. **Timeline**

The development of the POC of a judge’s dashboard took approximately 2-3 months, including data modelling and testing of the service. Building out the other POCs took 2 weeks including:&#x20;

![](https://lh7-rt.googleusercontent.com/docsz/AD\_4nXeZkKswme1NfJUlmh\_XDBSEYr8L1sUIctWiN1912YLaWEtjcL4L2JV7boakyiYi58M-4R6QtWXUfg5drZSJyaQD\_tJi7Ji7arjhYkfZNgLEXVMde92FNFbm5w7JSzjSt0TTELcvy1Y0jZhj4fcce3Dp5QyZ?key=BpTZdnbJWNo5iqrctUDI4Q)

8. **Status**

In the case of the bot to better understand the transitioning to the newer criminal laws, the application will undergo further testing and feature development, where another organisation will be refining its functionalities and ensuring it meets the users' needs. The OpenNyAI development team will continue providing clarifications and support during this phase.&#x20;

9. **Roadblocks & Learnings**

* Some applications/intent classification required multiple calls to the LLM. Making them more cost and resource intensive
