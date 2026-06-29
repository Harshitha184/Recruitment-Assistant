
import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from langfuse import observe
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@observe()
def _call_llm(prompt: str) -> list[str]:
    """Call Groq and parse a JSON list of skills from the response."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,    
        max_tokens=512
    )
    raw = response.choices[0].message.content.strip()

    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        skills = json.loads(raw)
        if isinstance(skills, list):
            return [str(s).strip() for s in skills if str(s).strip()]
    except json.JSONDecodeError:
        pass

    return re.findall(r'"([^"]+)"', raw)

@observe()
def extract_jd_skills(jd_text: str) -> set[str]:
    """
    Extract required skills from a Job Description.
    Called ONCE per screening session.
    """
    prompt = f"""You are a technical recruiter assistant.

Extract ALL technical and professional skills required in the job description below.
Include: programming languages, frameworks, tools, platforms, databases, cloud services,
methodologies, domain knowledge, certifications, and soft skills if explicitly mentioned.

Return ONLY a JSON array of skill strings. No explanation. No markdown. No extra text.

Example output: ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]

Job Description:
\"\"\"{jd_text[:3000]}\"\"\"
"""
    return set(extract_jd_skills_list(jd_text))


def extract_jd_skills_list(jd_text: str) -> list[str]:
    """Returns JD skills as a list (preserves order for display)."""
    prompt = f"""You are a technical recruiter assistant.

Extract ALL technical and professional skills required in the job description below.
Include: programming languages, frameworks, tools, platforms, databases, cloud services,
methodologies, domain knowledge, certifications, and soft skills if explicitly mentioned.

Return ONLY a JSON array of skill strings. No explanation. No markdown. No extra text.

Example output: ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]

Job Description:
\"\"\"{jd_text[:3000]}\"\"\"
"""
    return _call_llm(prompt)

@observe()
def extract_resume_skills(resume_text: str) -> set[str]:
    """
    Extract skills from a single resume.
    Called once per resume during the screening loop.
    """
    prompt = f"""You are a technical recruiter assistant.

Extract ALL technical and professional skills mentioned in the resume below.
Include: programming languages, frameworks, tools, platforms, databases, cloud services,
methodologies, domain knowledge, certifications, and any relevant skills.

Return ONLY a JSON array of skill strings. No explanation. No markdown. No extra text.

Example output: ["Python", "FastAPI", "PostgreSQL", "REST APIs"]

Resume:
\"\"\"{resume_text[:3000]}\"\"\"
"""
    return set(_call_llm(prompt))


def compute_skill_match(resume_skills: set[str], jd_skills: set[str]):
    """
    Case-insensitive intersection and difference.
    Returns (matched: set, missing: set) — values taken from jd_skills casing.
    """
    jd_lower   = {s.lower(): s for s in jd_skills}
    res_lower  = {s.lower() for s in resume_skills}

    matched = {jd_lower[k] for k in jd_lower if k in res_lower}
    missing = {jd_lower[k] for k in jd_lower if k not in res_lower}

    return matched, missing