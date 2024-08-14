# Climate Action with Wildlife First

**Community:** Wildlife First\


**Problem Statement**

Forest rangers in India face challenges in effectively addressing wildlife and conservation issues due to a lack of immediate access to comprehensive legal information. In most of their postings and patrolling areas, they lack the ability to communicate with other rangers, legal experts, or avail online services such as google or legal information forums. They often mistakenly book poachers under less stringent civil acts instead of more severe laws like the Arms Act, leading to inadequate legal action against offenders.&#x20;

**How was the problem addressed?**

A dashboard was developed for forest rangers, providing them with easy access to critical legal information and resources. This dashboard facilitates the following:

* Information Sharing: The dashboard allows forest rangers to share vital information and collaborate more effectively. They can document their experiences, share tips, and keep track of ongoing issues related to wildlife conservation.
* Conversation Threads: Rangers can maintain and revisit conversation threads, ensuring continuity in communication and better follow-up on previous discussions.
* Legal Reference: By digitising material on conservation laws (including bare acts and the two books published by Praveen Bhargav from Wildlife First), the dashboard enables rangers to quickly look up legal information. This feature helps rangers understand which laws to apply in various situations, such as distinguishing when to book poachers under the Arms Act instead of less stringent civil acts.
* Drafting Legal Documents: The dashboard assists rangers in drafting complaints and FIRs. It ensures that all necessary legal details are included, improving the accuracy and effectiveness of legal actions taken against offenders.\


To support these functionalities, Jugalbandi was integrated as the backend system for information retrieval. Jugalbandi accesses the digitised legal texts and provides rangers with relevant sections and laws in Kannada. This integration ensures that rangers have access to accurate and actionable legal information in their native language, which is crucial for effective on-ground implementation.



**What’s happening in the backend?**

1. Dashboard Integration: A dashboard was developed to allow forest rangers to share information, maintain conversation threads, and draft legal documents. This ensures effective collaboration and communication among rangers. Jugalbandi requires configuration to communicate with this dashboard.&#x20;
2. Legal Information Retrieval: When a ranger queries the system, Jugalbandi searches through the digitised legal texts (including the forest act, forest rights act, arms act and the provided books) to find relevant sections and laws. It retrieves the top five chunks of information that are most relevant to the query.
3. Metadata Filtering: Jugalbandi uses metadata such as section numbers and titles to enhance the search process, ensuring the retrieved information is precise and contextually relevant.
4. Language Support: Jugalbandi was configured to provide information in Kannada, ensuring that forest rangers can access legal details in their native language.
5. Automating Document Drafting: Once the relevant legal information is confirmed, the system assists in drafting complaints and FIRs by automatically filling out necessary fields based on the user-provided details and retrieved legal references.

**Implementation Requirements**

Tools:

* Digitised legal texts of wildlife laws.
* API services for information retrieval and dashboard integration.

Team:

* Developer for technical development and maintenance.
* Functional personnel to manage scripts, oversee testing, and maintain communication with the developer.

**Timeline**

* May: Initial meeting and knowledge transfer session.
* June: Deployment of a minor version of Jugalbandi.
* July: Further refinement and testing.
* August: Expected pilot launch.

**Status**

The project began in May 2024 with an initial meeting. A version of Jugalbandi was deployed within a month, and further development continued. By July, the team was refining the implementation and expected to pilot the solution by August. The project is currently in the testing and refinement phase.\


**Roadblocks & Learnings**

* Bandwidth Limitations: Limited resources and developer availability slowed down the development process.
