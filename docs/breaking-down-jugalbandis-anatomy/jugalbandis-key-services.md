# Jugalbandi’s Key Services

While the technical architecture of deploying and using Jugalbandi is slightly more complicated, we have tried to simplify the core features and relate them to everyday objects around us so that we can easily understand how each component functions and interacts within the system.

1\. Communication Channels: Think of this as the part of Jugalbandi that talks to different apps and systems. Whether it’s WhatsApp, Telegram, a website, or even business software like CRM systems, this component makes sure the messages are formatted correctly for whichever platform you’re using. It connects through the API service of Jugalbandi.

2\. Database (DB): We can imagine this as a cabinet where all the messages and information that pass through Jugalbandi are stored. It has instructions on how to set up, update, and manage the cabinet. Depending on the needs of the organisation using Jugalbandi (including their specific use case, geography and regulations), the way this data is handled can be customised.

3\. Indexer: Imagine the indexer as a librarian who organizes all the books in the library as per some categorisation. Similarly,the indexer arranges the information into neat, searchable chunks. This helps in finding the right information quickly. It breaks down the knowledge fed into Jugalbandi into smaller parts and adds labels to each part, making it easy to search and relate to other information.

4\. Retriever: The retriever is like a search engine within Jugalbandi. When you ask a question or look for information, the retriever searches through the organized chunks created by the indexer (the librarian) to find the relevant answers. It’s also responsible for making sure the search operations are efficient and tailored to specific needs.

5\. Retrieval-Augmented Generation (RAG): RAG is a key feature of Jugalbandi that allows any organization to conversationally query large datasets. It ensures that the answers are generated exclusively from the provided data, reducing the risk of misinformation and enhancing the accuracy of the responses.

\


<figure><img src="https://lh7-rt.googleusercontent.com/docsz/AD_4nXfxhTgVhYm_SYqGLMH9msE6UMSBtH1-KHn-aNJ3zILJuSbNI4hlNGN5xU9zR_DyO0szPXJHOiAj363xSZrvAOukDyy6616IjSfXz3BRk2wBJYlyl3TqYrcHUWab36lrsSVQZeiDpRHE-aV1GS9gy7F1Oog?key=BpTZdnbJWNo5iqrctUDI4Q" alt=""><figcaption></figcaption></figure>

_A Typical RAG Pipeline ; Source: Hirokazu Suzuki for_ [_Beatrust_](https://tech.beatrust.com/entry/2024/05/02/RAG\_Evaluation%3A\_Necessity\_and\_Challenge)

6\. Flow Manager: This component acts like a guide or a manager of conversations. It controls how the interaction flows, making sure the conversation is smooth and logical. For example, if you ask a vague question, it will prompt you for more details. It can categorize your needs, ask for more specific information, provide the right answers, and handle unexpected inputs. It’s highly customizable to fit different sectors and use cases.

7\. Language: The language component takes care of anything related to language. This includes translating languages, converting speech to text, and text to speech. It works with various services like Bhashini, Azure, or Google to handle these tasks.

\
