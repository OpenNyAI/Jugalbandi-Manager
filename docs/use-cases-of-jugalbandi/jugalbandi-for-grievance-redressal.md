# Jugalbandi for Grievance Redressal

**Community members involved:** CPGRAMS, Bhashini, Microsoft Research, Celebal Technologies

**Problem statement:**

Grievance redressal systems across various government departments and schemes face significant challenges. Citizens often struggle with the cumbersome process of registering grievances, as they must determine the appropriate department or scheme to address their issue. This complexity is compounded by the fact that each state, department, branch, and at times individual schemes can have their own Grievance Redressal Officer (GRO). For example, different government departments may oversee various hospitals. This lack of clarity about which department is responsible for a specific hospital complicates the grievance filing process.

These systemic issues highlight the need for a more user-centric approach to grievance redressal. The current process can be confusing and time-consuming for citizens, who may provide ambiguous details or be unsure of the correct department for their grievances. This situation underscores the necessity for a solution that can simplify the grievance registration process by accurately determining the relevant department, clearly structuring grievance descriptions for departmental officers, and automatically populating necessary forms based on user-provided descriptions.

**How was the problem addressed?**

Besides integration with LLM to interpret and classify grievance descriptions shared by the citizen accurately, the proposed solution had two more elements, including:&#x20;

* Intent Classification: Designing the solution  to continue asking follow-up questions until it gathers enough details to accurately understand the user's issue.&#x20;
* Retriever-Based Approach: Implementing a retriever system to index and retrieve relevant categories based on user inputs, ensuring precise category selection.
* Automated Form Filling: Utilising AI-generated inputs to automate the completion of grievance submission forms, reducing manual effort and improving efficiency.

**Scenario based User Journey with CPGRAMS Jugalbandi bot**

* User: "I have not received my ticket yet."
* Bot: "Thank you for reaching out. Could you please provide more details about the ticket you're referring to? Are you referring to a travel ticket such as flight, train etc. or an exam entrance ticket or grievance ticket etc.
* User: Travel ticket
* Bot: Awesome, please specify mode of transport
* User: train
* Bot: When and where was it issued, and have you received any confirmation or tracking details?"
* User: "I booked a train ticket two weeks ago, but I haven't received any email or physical ticket."
* Bot: "Understood. To assist you better, could you please specify the departure date and destination of your journey?"
* User: "Sure, the ticket was for a train journey from New Delhi to Mumbai on July 15th."
* Bot: "Based on the information provided, it appears that your grievance pertains to a 'Non-receipt of Train Ticket.' I will now categorize your grievance accordingly."

The bot automatically populates the required fields in CPGRAMS' submission form related to complaints about train tickets. It includes details such as the user's personal information, booking reference (if known), departure date, journey details, and specific grievances related to the non-receipt of the ticket. After confirming the details filled by the bot, the user clicks on the "Submit" button.

**What's happening in the backend?**

1. **Understanding Grievances:** When a user submits a grievance, Jugalbandi analyzes the provided details to understand the issue.\

2. **Finding Relevant Categories:** Jugalbandi searches through a dataset (such as an Excel or document file) with descriptions of different grievance categories to find matches.\

3. **Matching Similarities:** It compares the user's description with those in its database to identify the most similar categories.\

4. **Selecting the Best Fit:** The system ranks potential categories based on their relevance and selects the top-ranked category or provides options for the user to choose from.\

5. **User Confirmation:** To ensure accuracy, the system may ask the user to confirm the selected category or provide feedback, helping to clarify any uncertainties.\

6. **Automating Form Completion:** Once the category is confirmed, the system fills out the necessary fields in a format suitable for submission to the appropriate portal. (For eg - the CPGRAMS portal or Karnataka -[ Janaspandana](https://ipgrs.karnataka.gov.in/), [CM Helplines,](https://cmhelpline.tnega.org/portal/en/home) [IT Grievance ](https://eportal.incometax.gov.in/iec/foservices/#/fo-greivance/submit)etc.)&#x20;

**Implementation Requirements**

**Tools:**

* GPT-4 and GPT-3.5 models for parsing existing grievance categories and generating example grievances for each category
* Cleaned dataset for storing grievance categories.
* Jugalbandi’s Retriever component for category selection.
* Third party APIs for submission of grievances to the relevant departments

**Team:**

* Development team for bot implementation, including AI model integration and cloud migration
* Functional consultants for domain expertise in grievance management and workflow design.
* Quality assurance team for testing and validation of bot functionalities.

**Learnings**

* Retriever-based approaches can play a crucial role in improving how information is categorised and retrieved across various applications.&#x20;
* Incorporating user feedback into the retrieval process can help in identifying and correcting misclassifications or inaccuracies. When user interactions with the system are analyzed, developers can iteratively refine the retrieval methods to better meet user expectations.

\
