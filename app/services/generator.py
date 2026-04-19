import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_cv_improvements(cv_text: str, job_text: str):

    prompt = f"""
You are an expert CV writer and recruiter.

Analyze the CV against the job description.

Return ONLY valid JSON in this exact format:

{{
    "match_score": 85,
    "missing_skills": ["Python", "SQL"],
    "summary_rewrite": "Improved summary here",
    "improvement_suggestions": ["Suggestion 1", "Suggestion 2"],
    "cover_letter": "Professional cover letter here"
}}

CV:
{cv_text}

Job Description:
{job_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content