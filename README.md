# 🎯 AI Recruitment Assistant

An AI-powered Recruitment Assistant that automates resume screening, candidate ranking, skill matching, semantic search, and email generation using Large Language Models (LLMs), Vector Databases, and Generative AI.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-WebApp-red)
![Neon](https://img.shields.io/badge/PostgreSQL-Neon-success)
![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-orange)
![Groq](https://img.shields.io/badge/Groq-LLM-purple)
![LangChain](https://img.shields.io/badge/LangChain-Framework-green)

---

# 📌 Project Overview

Recruiting candidates manually is time-consuming and inefficient. This AI Recruitment Assistant automates the recruitment workflow by screening resumes against a job description using semantic similarity, extracting candidate information, ranking applicants, generating AI-powered emails, and storing structured and vector data in cloud databases.

---

# ✨ Features

- 📄 Upload multiple resumes (PDF, DOCX, TXT)
- 🤖 AI-based resume screening
- 🎯 Semantic similarity scoring
- 🧠 Automatic skill extraction
- 👤 Candidate name & email extraction
- 📊 Recruitment analytics dashboard
- 📈 Candidate ranking
- 🗄️ Candidate database management
- 📧 AI-generated shortlist/rejection emails
- ☁️ Cloud PostgreSQL (Neon)
- 🔍 Vector Search using Qdrant Cloud
- 🌙 Dark / Light Theme
- 📑 Screening report generation
- 📥 CSV and Report export

---

# 🏗️ System Architecture

```
                 User
                   │
                   ▼
          Streamlit Web Application
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
 Resume Parser  Skill Extractor  Name & Email Extractor
        │
        ▼
 Semantic Similarity (Sentence Transformers)
        │
        ▼
 Candidate Ranking
        │
 ┌──────┴───────────┐
 ▼                  ▼
Neon PostgreSQL   Qdrant Cloud
        │
        ▼
 Email Generator (Groq LLM)
```

---

# 🛠️ Tech Stack

### Frontend

- Streamlit
- HTML
- CSS

### Backend

- Python

### AI / ML

- Groq LLaMA 3
- Sentence Transformers
- LangChain
- Semantic Search

### Databases

- Neon PostgreSQL
- Qdrant Cloud

### Observability

- Langfuse

---

# 📂 Project Structure

```
AI-Recruitment-Assistant/

│── app.py
│── database.py
│── pipeline.py
│── matcher.py
│── utils.py
│── qdrant_db.py
│── email_generator.py
│── email_sender.py
│── report_generator.py
│── requirements.txt
│── README.md
│── .env.example
│── assets/
│── resumes/
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/Harshitha184/Recruitment-Assistant.git
```

Move into the project

```bash
cd Recruitment-Assistant
```

Create virtual environment

```bash
python -m venv venv
```

Activate virtual environment

Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
GROQ_API_KEY=

DATABASE_URL=

QDRANT_URL=

QDRANT_API_KEY=

LANGFUSE_PUBLIC_KEY=

LANGFUSE_SECRET_KEY=

EMAIL=

EMAIL_PASSWORD=
```

---

# 📸 Screenshots

Add screenshots here after deployment.

- Dashboard
- Resume Screening
- Recruitment Analytics
- Candidate Database
- Candidate Timeline
- Screening Report
- Email Generator

---

# 🌐 Live Demo

Coming Soon...

---

# 🔮 Future Enhancements

- Interview Scheduling
- Recruiter Login
- Candidate Comparison
- PDF Report Generation
- Docker Support
- CI/CD Pipeline
- Multi-user Authentication

---

# 👩‍💻 Author

**Vanaparthi Naga Harshitha**

Final Year B.Tech Student

AI | Generative AI | Python | LLM | LangChain

GitHub:
https://github.com/Harshitha184

---

# ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub.