from groq import Groq
from dotenv import load_dotenv
from langfuse import observe
import os
import re

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

@observe()
def generate_email(candidate_name, status):

    if status == "Similar":

        prompt = f"""
Write a professional recruitment email.

Candidate Name: {candidate_name}
Company Name: Eidiko Systems Integrators

The candidate has been shortlisted.

Rules:
- Do NOT write a subject line
- Do NOT start with "Subject:"
- Company name must only be "Eidiko Systems Integrators"
- Never mention any other company name
- Congratulate the candidate
- Professional tone
- Do NOT write any signature
- Do NOT write Regards
- Do NOT write Best Regards
- Do NOT write Thanks & Regards
- Do NOT write Sincerely
- Do NOT repeat candidate name at the end
- End the email immediately after the last paragraph
"""

    else:

        prompt = f"""
Write a professional recruitment email.

Candidate Name: {candidate_name}
Company Name: Eidiko Systems Integrators

The candidate was not shortlisted.

Rules:
- Do NOT write a subject line
- Do NOT start with "Subject:"
- Company name must only be "Eidiko Systems Integrators"
- Never mention any other company name
- Thank the candidate
- Encourage future applications
- Professional tone
- Do NOT write any signature
- Do NOT write Regards
- Do NOT write Best Regards
- Do NOT write Thanks & Regards
- Do NOT write Sincerely
- Do NOT repeat candidate name at the end
- End the email immediately after the last paragraph
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1024
    )

    email_content = response.choices[0].message.content

   
    email_content = email_content.replace(
        "[Company Name]",
        "Eidiko Systems Integrators"
    )

    email_content = email_content.replace(
        "Company Name",
        "Eidiko Systems Integrators"
    )

   
    email_content = re.sub(
        r"<[^>]+>",
        "",
        email_content
    )

   
    email_content = re.sub(
        r"\n\s*Dear\s+[A-Za-z\s]+\s*$",
        "",
        email_content,
        flags=re.IGNORECASE
    )

    # Remove unwanted closing phrases
    email_content = re.sub(
        r"(Sincerely,?|Best Regards,?|Regards,?|Thank You,?)\s*$",
        "",
        email_content,
        flags=re.IGNORECASE
    )

    email_content = email_content.strip()

    signature = """
--
Thanks & Regards,
HR Team
Eidiko Systems Integrators – IBM Software Services Practice
📧 hrteam.eidiko@gmail.com

🌐 www.eidiko.com
📱 +91 98765 43210
Suite 1, MJR Magnifique,
Khajaguda X Roads, Gachibowli,
Hyderabad – 500008, India
"""

    
    if "hrteam.eidiko@gmail.com" not in email_content.lower():
        email_content += signature

    print(email_content)

    return email_content