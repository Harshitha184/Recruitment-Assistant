# 🚀 AI Recruitment Assistant

An AI-powered recruitment automation platform that streamlines resume screening, candidate ranking, skill analysis, and recruitment communication using Semantic Search, Large Language Models (LLMs), PostgreSQL, and Vector Databases.

---

## 📌 Overview

AI Recruitment Assistant helps recruiters automate the hiring workflow by:

* Screening resumes against Job Descriptions
* Ranking candidates using Semantic Similarity
* Identifying Matched & Missing Skills
* Generating personalized recruitment emails
* Managing candidate records
* Generating recruitment reports
* Storing embeddings in a Vector Database for future semantic retrieval

The platform combines Generative AI, NLP, Semantic Search, PostgreSQL, and Qdrant to provide intelligent recruitment insights.

---

## ✨ Features

### 🤖 AI Resume Screening

* Upload multiple resumes
* Upload Job Description
* Semantic similarity-based candidate ranking
* AI-driven candidate evaluation

### 🧠 Skill Intelligence

* Extract skills from Job Descriptions
* Extract skills from candidate resumes
* Identify:

  * Matched Skills
  * Missing Skills

### 📊 Candidate Ranking

* Sentence Transformer embeddings
* Cosine Similarity matching
* Automatic scoring and ranking

### 📧 Automated Email Generation

* AI-generated acceptance/rejection emails
* Personalized candidate communication
* Bulk email support

### 🗄 Candidate Database

* PostgreSQL-based candidate storage
* Candidate history tracking
* Recruitment records management

### 📈 Recruitment Reports

* Candidate analytics
* Screening summaries
* Downloadable reports

### ⚡ Vector Database Integration

* Resume embeddings stored in Qdrant
* Semantic search ready architecture
* Scalable candidate retrieval

---

# 🏗 System Architecture

```text
Job Description
        │
        ▼
Sentence Transformer
        │
        ▼
JD Embedding
        │
        ▼
Cosine Similarity
        ▲
        │
Resume Embeddings
        │
        ▼
Candidate Ranking
        │
        ▼
PostgreSQL Storage
        │
        ▼
Recruitment Reports

Resume Embeddings
        │
        ▼
Qdrant Vector Database
```

---

# 🛠 Tech Stack

## Frontend

* Streamlit
* HTML
* CSS

## Backend

* Python

## AI / NLP

* Sentence Transformers
* Semantic Similarity
* Cosine Similarity
* Generative AI
* Prompt Engineering

## LLM

* Groq API

## Databases

### PostgreSQL

Stores:

* Candidate Name
* Email
* Resume Metadata
* Score
* Status
* Screening History

### Qdrant

Stores:

* Resume Embeddings
* Vector Metadata
* Semantic Search Data

## Email Services

* SMTP
* Gmail Integration

---

# 📂 Project Structure

```text
AI_RECRUITMENT_ASSISTANT/

├── app.py
├── database.py
├── qdrant_db.py

├── matcher.py
├── resume_parser.py

├── name_extractor.py
├── email_extractor.py

├── email_generator.py
├── email_sender.py

├── report_generator.py
├── utils.py

├── requirements.txt
├── .env

├── Eidiko_logo.png
```

---

# 🔍 AI Workflow

## Resume Screening

```text
Resume
    │
    ▼
Text Extraction
    │
    ▼
Embedding Generation
    │
    ▼
Semantic Similarity
    │
    ▼
Candidate Score
```

---

## Skill Analysis

```text
Job Description
       │
       ▼
Skill Extraction

Resume
       │
       ▼
Skill Extraction

Matched Skills
Missing Skills
```

---

## Email Automation

```text
Candidate Status
        │
        ▼
LLM Email Generation
        │
        ▼
SMTP Delivery
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/Harshitha184/Recruitment-Assistant.git

cd Recruitment-Assistant
```

---

## Create Virtual Environment

```bash
python -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key

EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

---

## Run PostgreSQL

Ensure PostgreSQL is running.

Database:

```text
recruitment_db
```

---

## Run Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

---

## Start Application

```bash
streamlit run app.py
```

---

# 📸 Screenshots

Add screenshots here:

### Home Page

![Home Page](screenshots/home.png)

### Resume Screening

![Resume Screening](screenshots/screening.png)

### Candidate Database

![Database](screenshots/database.png)

### Reports

![Reports](screenshots/reports.png)

---

# 🎯 Key Highlights

✅ AI-Powered Resume Screening

✅ Semantic Similarity Matching

✅ Candidate Ranking System

✅ AI Skill Analysis

✅ Automated Recruitment Emails

✅ PostgreSQL Integration

✅ Qdrant Vector Database

✅ Generative AI Integration

✅ End-to-End Recruitment Automation

---

# 📚 Future Enhancements

* Interview Scheduling
* Candidate Chatbot
* ATS Integration
* Recruiter Analytics Dashboard
* Advanced Vector Search
* RAG-based Candidate Retrieval
* Multi-Role Recruitment Support

---

# 👩‍💻 Author

**Naga Harshitha Vanaparthi**

AI / ML | Generative AI | Full Stack Development

---

# 📄 License

This project is developed for educational and recruitment automation purposes.
