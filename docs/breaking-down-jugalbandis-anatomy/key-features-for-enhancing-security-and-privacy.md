# Key Features for Enhancing Security and Privacy

The Jugalbandi framework incorporates some core features to ensure the security and privacy of the users. Some of these features are already in place, while others are planned for future implementation. Here, we elaborate on each feature with examples to show their practical application.

A.Redaction of Sensitive Data:

1. Sensitive Information Redaction: When a user inputs sensitive information such as an Aadhar number or phone number into the Jugalbandi system, this data is immediately flagged as sensitive.Before any data is stored in the database or sent to an LLM for processing, the Jugalbandi system automatically redacts sensitive information. This involves replacing the sensitive data with placeholders or masking it (for example, replacing an Aadhar number like 1234-5678-9123 with X's or other characters). Only the redacted data is stored in the database or transmitted to the LLM servers. This ensures that sensitive information is not exposed even if the database is compromised during transmission.When the LLM receives and processes the user's request, it does so without access to the actual sensitive information, working instead with the redacted data.&#x20;
2. Regex Pattern Matching: The Jugalbandi framework employs "Regex" (short for Regular Expressions) to automatically identify and remove sensitive data or profanity from user inputs by recording  certain patterns. These patterns serve as templates for identifying specific sequences of characters that match the criteria for sensitive data or offensive language. When a user inputs a message, the Jugalbandi system scans the text using the predefined Regex patterns. This allows the system to identify any parts of the message that match the patterns for sensitive data or profanity.

Once a match is found, the system automatically redacts or removes the identified sensitive data or offensive language.The cleaned message, free from sensitive data and profanity, is then logged and processed by the Jugalbandi system.&#x20;

\
B. Encryption:

1. Encryption of Sensitive Keys and Media: Jugalbandi encrypts sensitive keys, audio messages, and media messages, especially when migrating databases to the cloud.

When a user sends an audio message through the Jugalbandi bot on WhatsApp, this message is encrypted before being stored or transmitted. Even if intercepted, the encrypted message remains unreadable without the decryption key, protecting the user's privacy. Encryption is different from redaction in that redaction removes sensitive information from a dataset to prevent unauthorized access while encryption just transforms it into unreadable format.

2. Profanity Filter: If a user types a message containing offensive language, the profanity filter would detect and replace inappropriate words with asterisks or any other symbol, ensuring the conversation remains respectful and appropriate.

C. Controlled AI Model Access:

Restricted LLM Access: Jugalbandi ensures that OpenAI models only access prompts and data provided by the organization implementing the Jugalbandi framework, keeping sensitive information like WhatsApp or OS configurations secure.

For example, when using Jugalbandi to interact with an OpenAI model, the model only processes the user's questions and responses provided by the bot. It does not have access to the user's WhatsApp configuration or other underlying system details, preserving user confidentiality.

D. Strong Prompts: Jugalbandi uses strong prompts and prompt engineering techniques to control the output of large language models (LLMs) like GPT, Phi, and Llama, mitigating the risk of providing harmful or inappropriate responses. The aim is to ensure that the AI-generated responses remain accurate, relevant, and safe for users. By using well-engineered prompts, Jugalbandi ensures that the AI models produce outputs that are in line with the intended use case and user expectations. This reduces the likelihood of the AI generating inappropriate, irrelevant, or harmful responses. Additionally, we prefer integrating with proprietary LLMs like GPT, Phi, and Llama over open-source models. Proprietary models often come with additional safeguards, extensive training on diverse datasets, and better support for implementing prompt engineering techniques.

Below is an example of a strong prompt used by Jugalbandi:

_<mark style="color:green;">=GPT("You are grievance description writing bot whose job it is to write humanly readable, exhaustive and understandable descriptions of a category of grievance that may come under a particular Departments/Ministry of the Government of India. You will be provided a category of grievance in the form of “\<MINISTRY> | \<CATEGORY> | \<SUB CATEGORY> | \<SUB CATEGORY>… Sometimes there may be multiple SUB CATEGORY levels. You will include in your description what kind of Grievances the Sub Cattegory/Categories pertain to in such a way that a bot’s RAG system will be able to identify given a user query. You will only output a description and no other prefixes or sufixes. You will also include the different examples of ways in which people may refer to this grievance, for example, phone network could also be called network coverage and other terms. Be as exhaustive and all encompassing as possible. The Grievance category you must address is: " & J15251)</mark>_

* The prompt clearly defines the role of the LLM as a "grievance description writing bot," setting a specific context and purpose for the task. This helps the LLM understand the scope and limits of its response, ensuring it focuses on the task at hand.
* The prompt provides comprehensive instructions on what the LLM should do, including writing "humanly readable, exhaustive and understandable descriptions," and specifying the structure of the input ("\<MINISTRY> | \<CATEGORY> | \<SUB CATEGORY> | \<SUB CATEGORY>").&#x20;
* By instructing the LLM to include different examples of how people might refer to a grievance, the prompt ensures the responses are relevant and cover a wide range of possible user queries. This reduces the chances of the AI providing irrelevant information.
* The prompt's structure and specificity helps reduce the risk of generating harmful or inappropriate responses. By focusing on specific grievance categories and subcategories, the AI is less likely to produce outputs that are off-topic or inappropriate.
* The direction to "only output a description and no other prefixes or suffixes" ensures the AI's response is concise and to the point, avoiding unnecessary or irrelevant information that could confuse users or dilute the response's quality.

E. Data Residency Guarantees: All the data provided by Indian users reside within the boundaries of the country ensuring data sovereignty (in the case of deploying on Azure, the data usually resides within their South Indian data centres) &#x20;
