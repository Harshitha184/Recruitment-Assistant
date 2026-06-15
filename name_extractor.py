import re


SECTION_HEADERS = {
    "summary", "objective", "experience", "education", "skills", "projects",
    "certifications", "awards", "profile", "contact", "references", "languages",
    "interests", "publications", "volunteer", "work experience", "professional",
    "technical skills", "career", "about", "overview", "resume", "curriculum vitae", "cv"
}

NON_NAME_PATTERNS = re.compile(
    r'email|phone|mobile|tel:|linkedin|github|http|www\.|@|\.com|address|'
    r'\d{3,}|[+\(\)]{2,}|bachelor|master|degree|university|college',
    re.IGNORECASE
)

NAME_PATTERN = re.compile(
    r'^[A-Z][a-zA-Z\'\-\.]+(?:\s+[A-Z][a-zA-Z\'\-\.]+){1,3}$'
)


def clean_name(line):
    line = re.sub(
        r'^(name|candidate|applicant)\s*:\s*',
        '',
        line,
        flags=re.IGNORECASE
    )

    return line.strip()


def is_likely_name(line):

    line = clean_name(line)

    if not line:
        return False

    if NON_NAME_PATTERNS.search(line):
        return False

    if line.lower() in SECTION_HEADERS:
        return False

    words = line.split()

    if not (2 <= len(words) <= 4):
        return False

    if any(len(word) > 20 for word in words):
        return False

    if NAME_PATTERN.match(line):
        return True

    if all(word.isupper() for word in words):
        return True

    return False


def extract_candidate_name(resume_text):

    lines = resume_text.split("\n")

    for line in lines[:30]:

        line = clean_name(line)

        if is_likely_name(line):
            return " ".join(
                word.capitalize()
                for word in line.split()
            )

    return "Candidate"
'''def extract_candidate_name(resume_text):

    lines = resume_text.split("\n")

    for line in lines[:15]:

        line = line.strip()

        if not line:
            continue

        if is_likely_name(line):
            return line.title()

    return "Candidate"'''
def extract_candidate_name(resume_text):

    lines = resume_text.split("\n")

    for line in lines[:30]:

        line = clean_name(line)

        if is_likely_name(line):

            name = " ".join(
                word.capitalize()
                for word in line.split()
            )

            name = name.replace(
                "V Anaparthi",
                "Vanaparthi"
            )
            return name
        
    return "Candidate"