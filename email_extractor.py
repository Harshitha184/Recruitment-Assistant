import re
def extract_candidate_email(resume_text):
    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    matches = re.findall(
        pattern,
        resume_text
    )

    if matches:
        return matches[0]
    return ""