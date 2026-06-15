from langfuse import observe
from report_generator import generate_screening_report
from email_generator import generate_email
from resume_parser import extract_resume_text
from skill_extractor import (
    extract_jd_skills,
    extract_resume_skills,
    compute_skill_match
)
from matcher import calculate_match_score
from name_extractor import extract_candidate_name
from email_extractor import extract_candidate_email

@observe(name="Resume Analysis Pipeline")
def recruitment_pipeline(
    file_path,
    jd
):
    text = extract_resume_text(file_path)

    jd_skills = extract_jd_skills(jd)

    score = int(
        calculate_match_score(
            text,
            jd
        )
    )

    resume_skills = extract_resume_skills(text)
    matched, missing = compute_skill_match(
        resume_skills,
        jd_skills
    ) 
    candidate_name = extract_candidate_name(text)
    candidate_email = extract_candidate_email(text)
    return {
        "text": text,
        "score": score,
        "resume_skills": resume_skills,
        "matched": matched,
        "missing": missing,
        "candidate_name": candidate_name,
        "candidate_email": candidate_email
    }
@observe(name="HR Decision Pipeline")
def final_hr_workflow(
    df,
    jd,
    candidate_name,
    status
):
    report = generate_screening_report(
        df,
        jd
    )

    email = generate_email(
        candidate_name,
        status
    )

    return report, email