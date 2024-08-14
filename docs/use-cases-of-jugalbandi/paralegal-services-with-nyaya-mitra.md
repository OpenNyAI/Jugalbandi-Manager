# Paralegal Services with Nyaya Mitra

**Community Involved**

Outlawed, Nyaya Mitra Paralegals

**Problem Statement**

Paralegals play a crucial role in providing first-contact legal aid, such as helping with FIR registrations, protection orders, and connecting clients to NGOs and legal services. They gather essential information from clients to assist with legal matters. But the paralegals working with outlawed faced several challenges in their work, including difficulties with data collection due to time constraints and unsuitable user interfaces. Manual follow-ups for collecting complete data are inefficient, leading to incomplete reporting and data loss. There was a need for a system that could efficiently collect, manage, and track case data while being accessible and user-friendly for paralegals.&#x20;

**How was the problem addressed?**

To address these challenges, a conversational service was developed to streamline data collection and case management. The service includes functionalities such as voice-to-text conversion, asking follow-up questions to ensure complete data collection, and the ability to handle document uploads. It was designed to be user-friendly and responsive, catering to the specific needs of paralegals. The introduction of a dashboard further facilitated easy tracking and management of case data.

**User Journey**

Outlawed’s Jugalbandi based service facilitates with the training of the paralegals, helps them log their one-time services for clients in need of legal aid, as well has provides a more comprehensive monitoring technique to follow up on legal matters that may require multiple consultations over a prolonged period.&#x20;

Broadly, the actions of a paralegal when facilitating their clients through this conversational service would be as follows:&#x20;

Data Collection: Paralegals use the bot to collect client details, including name, contact number, gender, age, and a description of the legal issue.

Follow-Up Questions: The bot asks follow-up questions if necessary, ensuring all relevant information is collected.

Document Upload: Paralegals can upload documents, such as FIRs or RTI filings, directly through the bot.

Client Database: Once client details are logged, they are stored permanently in the database, allowing for easy follow-up and tracking of repeat clients.

Periodic Follow-ups: After a specified period, the action items for the paralegals are highlighted for them to go back to their clients and reassess the need for any intervention.&#x20;

**What’s happening in the backend?**&#x20;

Understanding Grievances: The bot analyzes user-provided details to understand the issue.

Finding Relevant Categories: It searches through a dataset with descriptions of different legal categories to find matches.

User Confirmation: The system may ask the user to confirm the selected category or provide feedback to ensure accuracy.

Automating Form Completion: Once confirmed, the bot fills out necessary fields for submission to Outlawed’s coda dashboard. \


**Status**

With a launch planned for late August 2024, the bot is currently being tested and refined based on feedback from paralegals. It has shown promise in improving data collection accuracy and efficiency. Discussions are ongoing with cloud service providers for hosting and maintaining the bot.

**Implementation Requirements**

Team:&#x20;

1 developer for building, deploying and managing the Jugalbandi based service

2 functional personnel familiar with the operations of paralegals and their community’s requirements to design the flows and oversee testing and refinement

5-8 paralegals to test and provide feedback

**Timelines**

4 weeks including:

1 week to create user flows and relay them to the development team

1 week to build a preliminary prototype of the indicated flows (including a feature addition of accepting user documents, apart from the KBs that were provided during the creation of the bot)

2 weeks for testing and refinement based on the feedback of the paralegals

**Roadblocks and Learnings**

**Data Collection Issues:** Initial form-based data collection was ineffective due to time constraints and user interface challenges, which resulted in inadequate data being captured and multiple follow ups with the client.&#x20;

**Voice-to-Text Difficulties**: Ensuring accurate voice-to-text conversion for various languages was challenging, particularly in the matter of interpreting dates from the voice notes.

**Training Needs:** Initial testing emphasised the importance of training paralegals on the significance of data collection and proper usage of the bot.

\
