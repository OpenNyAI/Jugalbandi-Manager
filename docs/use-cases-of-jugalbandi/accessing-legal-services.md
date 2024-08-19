# Accessing Legal Services

1. **Community members involved**

CADRE, CORD, Presolv 360, Sama, Beckn, Agami, Thoughtworks, PUCAR&#x20;

2. **Problem statement**\
   Most Indian citizens face significant challenges in accessing effective dispute resolution services, particularly through institutions that operate independent of courts. Traditional legal processes can be complex, time-consuming, and expensive, making it difficult for people to resolve disputes efficiently. This inaccessibility often leaves individuals without the necessary support to address their legal issues, such as cheque bouncing disputes, which can have serious financial and legal implications.
3. **How the problem was addressed**

The project aimed to create a solution that simplifies and makes the services of Online Dispute Resolution (ODR) providers more accessible. Building on the concept of Jagrit bots, which provide users with legal information, the project focused on developing a platform where users can take practical steps based on the information they receive.

Taking the process of dealing with cheque bounce disputes as the unit of change, this solution would allow a user to:&#x20;

1. Seek information on legal matters arising from a bounced cheque.
2. Draft a legal notice demanding payment for the bounced cheque.
3. Access services of an ODR platform to resolve the dispute.

\
Jugalbandi could readily deploy a conversational bot that could answer queries based on the provided knowledge base of cheque bounce disputes. For the discovery and availing of legal services, an adaptation of the Beckn protocol was utilised. The[ Beckn Protocol](https://becknprotocol.io/beckn-made-simple/) is an open and decentralised protocol that facilitates seamless transactions across various sectors by enabling the creation of peer-to-peer digital networks. It allows businesses and service providers to be universally discoverable from any Beckn-enabled application, removing the need for centralised platforms. \


The [PULSE protocol](https://pucar-initiatives.glide.page/dl/dcc150), is an adaptation of Beckn for legal services, it enables any user to discover and avail the services of various legal service providers, but existing implementations of the [protocol](https://experience-guide.becknprotocol.io/ODR) (on the seeker side, for those who intended to use the protocol to discover legal service providers) operate as web applications that use drop down menus and static buttons, all in English.To make the protocol demonstration more user-friendly, Jugalbandi was configured to enable users to access services, such as those provided by Online DR platforms.

4. **User Journey**\
   Information on cheque bouncing disputes that were publicly available from credible sources, as well as PUCAR’s research on such disputes were synthesised into tables that could act as an effective knowledge base.\
   \
   [Scripts](https://docs.google.com/document/d/1BrNKoMIwOVc6lTNUrL58jPIL2Tb-vbl7KZurWz8UAfg/edit?usp=sharing) detailing users' possible journeys were created, along with flow-charts that could help developers quickly familiarise themselves with the configurations required to the flow states of the Jugalbandi manager.&#x20;

\
A brief summary of the user journey is as follows, for the more detailed flow refer to the appendix:&#x20;

1. User Initiates Interaction:

* The user receives a notification about a bounced cheque on the WhatsApp bot.
* The bot asks the user for their preferred language, name, and place of residence.

2. Bot Provides Options:

* The bot informs the user it can assist with connecting to a banking representative, providing legal rights information, or seeking legal recourse.
* The user opts to get legal information on what can be done about the bounced cheque.

3. Legal Information and Actions:

* The bot explains the legal procedures and consequences of a bounced cheque, including the need to draft a demand notice.
* The user can choose to draft a legal notice, consult a lawyer, or use an Online Dispute Resolution (ODR) platform.

4. Action Execution:

* If the user chooses to draft a notice, the bot collects necessary details and uses an API of a third-party service (such as [EazyDraft)](https://eazydraft.com/) to create the draft.
* If the user needs a lawyer, the bot assists in discovering available legal service providers and scheduling appointments.

5. **What’s happening in the backend?**&#x20;

* Understanding User Request/Concern: Jugalbandi parses user inputs regarding cheque bounce disputes. By employing cost-effective LLMs such as GPT- 4o mini or 3.5, it identifies the user's specific needs, whether it is seeking information, drafting a legal notice, or consulting legal services. The prompt that allows Jugalbandi to understand the context of user’s messages for this use case can be found in the appendix. &#x20;
* Optimising Information Retrieval: The knowledge base, consisting of [spreadsheets ](https://docs.google.com/spreadsheets/d/16d23VrUsJ-ilU4I4znTwFwyWYNiAp-mCvRRWosXTmUQ/edit?usp=sharing)and PDFs, was pre-formatted for optimal use by Jugalbandi. The information is divided into small, easy-to-parse pieces to make searching easier. Through a process of testing and refining, it was decided that the five best chunks of information will be considered, so that it most closely matches the user's question. These 5 chunks are then used to generate answers using LLMs.&#x20;
* API Integrations: This instance of Jugalbandi requires extra configuration to call relevant third party APIs (like PULSE, EazyDraft etc).  These APIs provide additional information that Jugalbandi can use as dynamic knowledge bases. With these integrations, Jugalbandi can offer not only the information from its internal RAG pipeline but also provide data and services from various legal platforms and service providers. This makes Jugalbandi more versatile and able to deliver a wider range of information and services.

6. **Implementation Requirements:**&#x20;

_Tools:_&#x20;

* API services to communicate with a whatsapp business account & a testing environment for PULSE APIs.&#x20;
* Access to the Beckn [sandbox](https://registry.becknprotocol.io/login) to test the PULSE protocol

_Team:_&#x20;

* Developer to handle the technical development and maintenance.&#x20;
* Functional personnel to develop scripts, manage knowledge bases, oversee testing, and maintain communication with the developer.

7. **Timeline: 2 weeks, including:**&#x20;

<figure><img src="https://lh7-rt.googleusercontent.com/docsz/AD_4nXdp9RPraBB5ubv_4nv71RC2ercEP9MFFLH9VAKpjY66owa4HlVVjliFISltv0tdlIXz3UnxKZn54US4lxcH-bWSAG8cw88gyG4y4r4E9G2IuPzeAarZyFWRTnykdopana0sFjnlZwAi2QhqKbH3dKj4pUg?key=BpTZdnbJWNo5iqrctUDI4Q" alt=""><figcaption></figcaption></figure>

8. **Status**

Upon development and testing of 2 bots that leveraged the PULSE protocol, ie, the cheque bounce bot and a helper bot to aid small businesses and aspiring entrepreneurs navigate legal/regulatory hurdles. The code repository for the POC can be found in the [OpenNyAI Github ](https://github.com/OpenNyAI/pulse/)page.&#x20;

9. **Roadblocks & Learnings**&#x20;

One of the hurdles encountered during the implementation of this whatsapp bot, was in the usage of forms (or whatsapp ‘flows’), a pop-up template to collect information from the user. This form was used to collect information on the complainant details, respondent details and the dispute details.&#x20;

* While the whatsapp form operated without a glitch for most devices, for some devices (that didn’t have any correlation of the OS used, version of whatsapp etc.) returned the parameters of the form itself, instead of the information entered by the user. Example: The form returned “form.name”, instead of the name interred by the user in the respective field, the field itself was returned to the FSM. While the root issue of this bug hasn’t yet been uncovered, the issue has been escalated to the service provider facilitating managed services for the Meta whatsapp APIs, as well as the team from Meta responsible for the whatsapp flows.\

* Implementing the PULSE APIs presented challenges, particularly with [fields](https://docs.google.com/spreadsheets/d/1BagyiuqsQ0dbl--9S98gBwuFn1maCRioiVxaile29y0/edit?usp=sharing) like Dispute details and consent forms, which required the use of [X-Forms](https://www.w3.org/TR/2003/PR-xforms-20030801/slice2.html)[Broken link](broken-reference "mention"). [The Beckn Sandbox](https://github.com/beckn/beckn-sandbox) did not support rendering these forms for collecting information outside [Beckn’s core specifications.](https://github.com/beckn/protocol-specifications/tree/master/schema)\
  After consulting with the Beckn team, it was decided to simulate the collection of this information by creating mock data to represent the required fields. This approach allowed the team to integrate and test the PULSE API flow without relying on the unsupported functionalities of the Beckn Sandbox.\
