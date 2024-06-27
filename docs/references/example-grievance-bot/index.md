---
layout: default
title: Example Grievance Bots
---

This is an example of building a grievance bot. We consider an organization like [CPGRAMS](https://pgportal.gov.in/) that allows Indian citizens to lodge complaints with any department of the government. 

Review the notbooks [indexer.ipynb](indexer.html) and [retriever.ipynb](retriever.html) in this directory for the entire source code.

# Final User experience

```bash
# TODO - add screenshots
```

# Step 1: Data Indexing Pipeline

## Intial Data

We scrape the following information from the CPGRAMS website:
```bash
# TODO - add sample csv data
```

## Schema for Vector DB

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

## Data Augmentation

## Data Indexing

# Step 2: Data Retriever Pipeline

```bash
# TODO - screenshot of the overview
```

## Summarizing details provided so far

## Fetching matching records from VectorDB

## Ask clarifying question or are we done?

## Asking for details required to lodge the complaint.


