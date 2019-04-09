# seeking_alpha_crawler
## Summary
In this repo, we implemented a crawler to crawl seekingalpha website data using scrapy. Data we collected from seeking alpha is stored in a database called earningcall_transcripts.db with 8 tables: companies, transcripts, internal_participants, external_participants, question_answers, question_answer_dialogues, presentations and presentation_dialogues.

## Database
- companies
  
  companies table contains basic information of a company like its name, stock name and company id . A single company appears only once in the table. Corresponding earning results of the company can be identified by company_id column.

- transcripts

  transcripts contains the corresponding article details like the article published date, published quarter, article url, audio call url and company id. Each row represents one article and can be identified by report_id.

- internal_participants

  internal_participants consists of all the company related people participated in the call. All the company related people are logged to company_participants column. 

- external_participants

  external_participants consists of people from different companies other than the host company who participated in the call.All the company related people are saved to external_participants column. 
  
- question_answers

  question_answers table acts as a connecting table between an article and the QA dialogues occured during the call. It consists of id and transcript_id columns.

- question_answer_dialogues

  question_answer_dialogues consists of all the dialogues occured in QA session. It consists of qa_id which is corresponds to the id of the question. internal_person_id and external_person_id columns are used to identify the person who is speaking. Dialogue column collects the conversation.
  
- presentations

  presentations table acts as a connecting table between an article and the presentation dialogues occured in the article. It consists of id and transcript_id. 
  
- presentation_dialogues

  presentation_dialogues consists of all the dialogues occured in presentation session.


## Files
Please see blow for the important files that are frequently modified in this repo.

- seekingalpha.py

  Implementation of seekingaplha crawler are contained in this file. First crawler logs into seekingalpha using credential stored in environment file. Then it starts to crawl url stored in the dictionary custom_settings. This file is located in spiders folder.

- models.py

  Database is implemented using ORM in this file. Every table in the database is associated with one class.

- items.py

  Scrapy uses item class to define common output data format. All the information in items will be stored into different tables in persistDatabase.py

- persistDatabase.py

  This file contains code used to store crawled information into database.

- settings.py

  This file is used to define general settings for the crawler, including where database and images are stored.

