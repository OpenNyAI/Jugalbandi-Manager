---
title: Example Grievance Bots
---

# Example Grievance Bots

This is an example of building a grievance bot. We consider an organization like [CPGRAMS](https://pgportal.gov.in/) that allows Indian citizens to lodge complaints with any department of the government.

Review the notbooks [indexer.ipynb](../../../../references/example-grievance-bot/indexer.html) and [retriever.ipynb](../../../../references/example-grievance-bot/retriever.html) in this directory for the entire source code.

## Final User experience

|                                                       |                                                       |                                                       |
| :---------------------------------------------------: | :---------------------------------------------------: | :---------------------------------------------------: |
| ![](../../../../assets/grievance-bot/whatsapp-1.jpeg) | ![](../../../../assets/grievance-bot/whatsapp-2.jpeg) | ![](../../../../assets/grievance-bot/whatsapp-3.jpeg) |

## Step 1: Data Indexing Pipeline

### Intial Data

We scrape the following information from the CPGRAMS website:

| Ministry                             | Category                                                                                 | Subcategory 1                                       | Subcategory 2                                  | Subcategory 3            | Subcategory 4  | Subcategory 5     |
| ------------------------------------ | ---------------------------------------------------------------------------------------- | --------------------------------------------------- | ---------------------------------------------- | ------------------------ | -------------- | ----------------- |
| Department of Science and Technology | Removed/ Retrenched Employee/ Service Matter/ Transfer/ Compassionate Appointment/ other | SMP Division                                        | Survey of India                                | Chhattishgarh GDC Raipur |                |                   |
| Department of Science and Technology | Allegation of Harassment/ Atrocities                                                     | Cash ACR Library                                    |                                                |                          |                |                   |
| Housing and Urban Affairs            | NBCC                                                                                     | NBCC                                                | Regarding Contract/ Tax/ Bill Payment/ Project | INDIA                    | Madhya Pradesh |                   |
| Ministry of Panchayati Raj           | Corruption Related to Panchayats                                                         | Panchayat Embezzlement or Misappropriation of Funds | Madhya Pradesh                                 |                          |                |                   |
| Telecommunications                   | Employee Related / Services Related                                                      | Pending any type of Bill/dues for payment           |                                                |                          |                |                   |
| Housing and Urban Affairs            | NBCC                                                                                     | NBCC                                                | Regarding Contract/ Tax/ Bill Payment/ Project | INDIA                    | Delhi          | East Kidwai Nagar |
| Department of Ex Servicemen Welfare  | Service Related                                                                          | Outstanding Dues                                    | Monetary Allowance for Gallantry Awards        | Navy                     |                |                   |
| NITI Aayog                           | Administration and Establishment Matters                                                 | Recruitment                                         | Young Professionals and Consultants            | Declaration of Result    |                |                   |
| Housing and Urban Affairs            | NBO (National Buildings Organisation)                                                    | Various Service Matters                             | Service                                        |                          |                |                   |
| Housing and Urban Affairs            | Directorate of Estates                                                                   | Allotment Related-Delhi                             | Type-I & II                                    | Waiting List             |                |                   |

### Data Augmentation

We have generated an elaborate description for each grievance by using GPT-4, with appropriate system prompt and providing the ministry name, category and subcategories. The generated description is in following format:

| Ministry           | Category                            | Subcategory 1                             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------ | ----------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Telecommunications | Employee Related / Services Related | Pending any type of Bill/dues for payment | <p>This grievance category pertains to issues related to pending bills or dues for payment in the telecommunications sector, specifically in relation to employees or services.<br>Individuals may file complaints if they have not received bills for their telecommunications services, if there are errors or discrepancies in the billing, if they are facing challenges in making payments for their bills, or if there are delays in the processing of payments resulting in overdue dues.<br>Some common examples of how people may refer to this grievance include:<br>- Unpaid bills for telecommunications services<br>- Overdue payments for phone/internet services<br>- Outstanding dues for mobile network usage<br>- Pending invoices for employee phone plans<br>It is important for the Department/Ministry of Telecommunications to address these grievances promptly in order to ensure smooth operation of services and fair treatment of employees.</p> |

### Schema for Vector DB

We need to make this available in a VectorDB to fetch the data based on similarity. We create the following schema. `embedding` is the vector representation of `description` column.

```
class GrievanceCategory(Base):
    __tablename__ = "grievance_category"
    id = Column(String, primary_key=True)
    ministry = Column(String)
    category = Column(String)
    subcategory = Column(ARRAY(String))
    description = Column(String)
    embedding = mapped_column(Vector(1536))
    fields = Column(ARRAY(JSON))
```

`fields` stores an array of fields that the user needs to provide to lodge their compliant.

### Data Indexing

## Step 2: Data Retriever Pipeline

![](../../../../assets/grievance-bot/retriever-flow.jpg)

Conversation so far,

```python
llm_system_prompt = sm(system_prompt)
messages = conversation_history + [llm_system_prompt]
pprint(messages)
```

```json
[
    {
        "content": "You are a helpful assistant, the CPGRAMS bot, working with the Prime Minister of India's office. Your role is to help users share their grievances on a grievance redressal platform for the Government of India. You will not offer any solutions for their grievance. You will merely try to extract as much information as possible to allow a grievance officer to deal with the grievance effectively. Current date: 2024-04-25",
        "role": "system"
    },
    {
        "content": "Hi, How can I help you?",
        "role": "assistant"
    },
    {
        "content": "I am unable to access my PAN card from digilocker",
        "role": "user"
    },
    {
        "content": "Analyze the above conversation in detail and give your analysis. Your analysis should be detailed enough such that it could be used to determine the grievance category from a database. Do not try to determine the grievance category in this step. Current date and time: 2024-04-25 15:16:17. Process any date and time related information in the conversation.",
        "role": "system"
    }
]
```

### Summarizing details provided so far

```python
summary, cost = llm(messages, model="gpt-4-turbo-preview")
print(summary)
```

```
The user's grievance revolves around an issue with accessing their Permanent Account Number (PAN) card from DigiLocker. DigiLocker is a digital platform launched by the Government of India aimed at ensuring that citizens have access to authentic digital documents in a digital wallet provided by the government. The user's inability to access their PAN card from this platform can be attributed to several potential causes, such as technical glitches within the DigiLocker system, issues related to the linking of the PAN with the user's DigiLocker account, or discrepancies in the user's personal information that may be causing a mismatch.

Key elements to extract and analyze for effectively categorizing and addressing this grievance include:

1. **Nature of the Issue**: The problem is specifically related to accessing a government-issued document (PAN card) through a government-provided digital service (DigiLocker). This indicates that the grievance falls within the domain of digital governance and e-services.

2. **Services Involved**: The grievance involves two critical services - the issuance and management of PAN cards, which is typically overseen by the Income Tax Department, and the DigiLocker service, which is an initiative under the Ministry of Electronics and Information Technology (MeitY). Understanding the interplay between these services is crucial for addressing the grievance.

3. **Possible Causes**: The issue could stem from technical problems (e.g., server downtime, app malfunctions), user account issues (e.g., incorrect login credentials, PAN not linked to DigiLocker), or data mismatches (e.g., discrepancies in personal details between PAN records and DigiLocker).

4. **Information Required for Resolution**: To effectively address the grievance, additional information might be needed, such as error messages received, steps already taken by the user to try and resolve the issue, and confirmation of personal details for verification purposes.

5. **Impact on the User**: The inability to access the PAN card digitally can affect the user's ability to perform various financial transactions and comply with statutory requirements, highlighting the urgency of resolving the issue.

6. **Potential Departments for Escalation**: The grievance may need to be escalated to the Income Tax Department for issues related to PAN details and to the technical team behind DigiLocker for problems related to the digital platform itself.

This detailed analysis helps in understanding the complexity of the issue, which spans across technical, procedural, and personal information verification aspects, requiring a coordinated response from multiple government departments.
```

### Fetching matching records from VectorDB

```python
top_k = 10
relevant_categories = session.scalars(
    select(GrievanceCategory)
    .order_by(GrievanceCategory.embedding.l2_distance(summary_embedding))
    .limit(top_k)
).all()
```

```
[<GrievanceCategory(ministry=Unique Identification Authority of India, category=Linking of Aadhaar related issues, subcategory=['Linking of Aadhaar with PAN']>,

<GrievanceCategory(ministry=Central Board of Direct Taxes (Income Tax), category=PAN Issues, subcategory=['Other']>,

<GrievanceCategory(ministry=Central Board of Direct Taxes (Income Tax), category=PAN Issues, subcategory=['Delay in PAN issues']>,

<GrievanceCategory(ministry=Central Board of Direct Taxes (Income Tax), category=PAN Issues, subcategory=['Wrong PAN number allotted']>,

<GrievanceCategory(ministry=Central Board of Direct Taxes (Income Tax), category=PAN Issues, subcategory=['Mistakes in PAN card']>,

<GrievanceCategory(ministry=Central Board of Direct Taxes (Income Tax), category=PAN Issues, subcategory=['Same PAN numbers allotted to multiple users']>,

<GrievanceCategory(ministry=Ministry of Electronics & Information Technology, category=Digital Services (CSC/MyGov/NeGD/NIC), subcategory=['NeGD', 'DigiLocker']>,

<GrievanceCategory(ministry=Labour and Employment, category=Compliance related Issues, subcategory=['UAN related issues/KYC related issues.']>,

<GrievanceCategory(ministry=Telecommunications, category=Mobile Related, subcategory=['AADHAR Linking/Documents verification']>,

<GrievanceCategory(ministry=Unique Identification Authority of India, category=Linking of Aadhaar related issues, subcategory=['Linking of Aadhaar with Bank Account']>]
```

### Ask clarifying question or are we done?

```python
def determine_grievance_bucket_and_followup_questions(
    conversation_history, possible_buckets
):
    system_prompt = """You are a helpful assistant, the CPGRAMS bot, working with the Prime Minister of India’s office. Your role is to help users share their grievances on a grievance redressal platform for the Government of India.
    Here is a set of possible grievance buckets in which the user could raise a grievances. 
    Possible grievance buckets:
    {options}
    
    Analyze the conversation history and the user input. 
    Your primary task is to determine most relevant grievance bucket in which the user query can fall.
    Do not recommend grievance buckets if you do not have enough required information or you are not sure about. 
    Do not recommend grievance buckets that do not satisfy all the categories and subcatgories according to the information provided by user.
    If you think you do not have enough information, generate a short follow up question that can be asked to the user whose response can help in determining the grievance bucket.
    Also, generate an brief empathetic prefix message to show to the user before asking the followup question.
    Do not recommend grievance buckets if multiple grievance buckets from the list satisfing the criteria given by required information. Ask the user to provide more information.
    The follow up question should be very diverse. 
    You can ask upto 1 follow up question, not more than 1. 
    The follow up question should be very basic, do not ask question that you think a 15 year old would not be able to answer.
    You will not offer any solutions for their grievance. You will merely try to extract as much information to exactly determine the grievance bucket.
    Since you are not offering any solutions, you can ask any question that you think can help you determine the grievance bucket.
    Analyze and tell why you think the grievance falls under the grievance bucket. If you don't think any grievance bucket from the provided list is relevant, tell the reason for it.


    Give the output in the following json format:
    {{
        "grievance_bucket": 
            {{
                "bucket_id": "bucket_id",
                "ministry": "ministry",
                "category": "category",
                "subcategory": ["subcategory"],
                "description": "description"
            }}
        ,
        "follow_up_questions": [
            "question 1"
        ],
        "user_message": "Empathetic prefix message to show to user in a conversational manner. The message should be short and include emojis to show empathy and make the user feel comfortable."
    }}
    Provide empty list if no follow up questions are mentioned.
    Provide none if no grievance buckets are mentioned by user. Do not generate new grievance buckets. Only consider the grievance buckets provided.
    """
    system_prompt = sm(system_prompt.format(options=possible_buckets))
    buckets_and_questions, cost = llm(
        messages=conversation_history + [system_prompt],
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
    )
    response = json.loads(buckets_and_questions)
    return response, cost

grievance_buckets, _ = determine_grievance_bucket_and_followup_questions(
    conversation_history, possible_buckets_text
)
pprint(grievance_buckets)
```

```json
{
    "follow_up_questions": [],
    "grievance_bucket": {
        "bucket_id": "6",
        "category": "Digital Services (CSC/MyGov/NeGD/NIC)",
        "description": "The DigiLocker service provided by the National e-Governance Division (NeGD) under the Ministry of Electronics & Information Technology allows users to store, access, and share digital copies of important documents and certificates. Users may have the following grievances related to DigiLocker:\n1. Difficulty in accessing or signing up for DigiLocker account\n2. Issues with uploading or downloading documents on DigiLocker\n3. Concerns about the security and privacy of personal information stored on DigiLocker\n4. Problems with linking DigiLocker to other government services or platforms\n5. Unauthorized access to DigiLocker account\n6. Technical glitches or errors while using DigiLocker\n7. Unclear guidelines or instructions on how to use DigiLocker effectively. Alternate terms for DigiLocker may include digital locker, online document storage, digital document repository, etc.",
        "ministry": "Ministry of Electronics & Information Technology",
        "subcategory": [
            "NeGD",
            "DigiLocker"
        ]
    },
    "user_message": "I'm really sorry to hear that you're facing issues with accessing your PAN card from DigiLocker. Let's get this sorted."
}
```

### Asking for details required to lodge the complaint.

```python
def generate_field_questions(grievance_bucket, required_fields, conversation_summary):
    system_prompt = """
    You are a helpful assistant, the CPGRAMS bot, working with the Prime Minister of India’s office. Your role is to help users share their grievances on a grievance redressal platform for the Government of India.
    
    You'll be grievance bucket, containing ministry name, category, sub categories and description of grievance in which user can file grievance.
    You're also provided the fields required to file the grievance.
    You'll be provided the conversation summary of the user.
    Analyze the conversation summary and determine the value of fields. 
    Some fields might require description of the grievance, so infer the description on your own instead of asking the user.
    Analyze and determine if value of all the mandatory fields are present. 
    Analyze the grievance bucket, and generate an brief empathetic prefix message to show to the user before asking the followup question.
    Everything should be brief. 
    If value of all mandatory fields are present, set the value of mandatory_data_present to True, else set it to False.
    If value of all mandatory fields are present, you can tell user in the brief emphatic message that all the required fields are present and ask them to confirm the values of the fields to proceed filing the grievance. 
    Do not generate more than 1 follow up question.
    Your task is to restructure the follow up in json format as shown below:
    {{
        "grievance_bucket": 
            {{
                "bucket_id": "bucket_id",
                "ministry": "ministry",
                "category": "category",
                "subcategory": ["subcategory"],
                "description": "description"
            }}
        ,
        "follow_up_questions": [
            "question 1"
        ],
        "user_message": "Empathetic message to show to user in a conversational manner. The message should be short and include emojis to show empathy and make the user feel comfortable."
        "field_data": 
            {{
                "field_1": "field_1_value", # field_1 is the name of field and field_1_value is the value. use none if the value is not present.
                "field_2": "field_2_value"
            }}
        ,
        "mandatory_data_present": True/False # Set it to True if value for all the mandatory fields are present, else set it to False.
    }}

    Provide empty list if no follow up questions are needed.
    
    """
    user_message = f"""
    Grievance bucket:
    {grievance_bucket}

    Required fields:
    {required_fields}

    Conversation Summary:
    {conversation_summary}
    """
    response, cost = llm(
        messages=[sm(system_prompt), um(user_message)],
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
    )
    response = json.loads(response)
    return response, cost

field_questions, _ = generate_field_questions(user_choice, required_fields, summary)
pprint(field_questions)
```

```json
{
    "field_data": {
        "Device_Used": "none",
        "Document_Type": "PAN card",
        "Error_Message": "none",
        "Internet_Connection": "none",
        "Issue_Details": "Inability to access PAN card on DigiLocker, potentially due to technical issues, account problems, or discrepancies in linking PAN with DigiLocker account."
    },
    "follow_up_questions": [],
    "grievance_bucket": {
        "bucket_id": "6",
        "category": "Digital Services (CSC/MyGov/NeGD/NIC)",
        "description": "The user is experiencing difficulty accessing their Permanent Account Number (PAN) card on DigiLocker. This issue may be due to technical glitches, user account problems, or discrepancies in linking the PAN with the DigiLocker account. Access to the PAN card is crucial for the user for various financial transactions and identity verification processes.",
        "ministry": "Ministry of Electronics & Information Technology",
        "subcategory": [
            "NeGD",
            "DigiLocker"
        ]
    },
    "mandatory_data_present": true,
    "user_message": "We understand how important it is for you to access your PAN card on DigiLocker and the inconvenience this issue may be causing you. Rest assured, we're here to help. All the required details for filing your grievance are present. Could you please confirm the details so we can proceed with filing your grievance?"
}
```
