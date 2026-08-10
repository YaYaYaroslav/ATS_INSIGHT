from app.services.job_parser import parse_job_description

SAMPLE_JOB = """
We are looking for a Backend Developer with 3+ years of experience.

Requirements:
Python, FastAPI, PostgreSQL, Docker

Nice to have:
Kubernetes, AWS

Responsibilities:
- Design and build REST APIs
- Work with PostgreSQL databases

Bachelor's degree in Computer Science or related field.
"""


def test_parse_job_extracts_required_skills():
    result = parse_job_description(SAMPLE_JOB)
    assert "python" in result["required_skills"]
    assert "fastapi" in result["required_skills"]


def test_parse_job_extracts_experience_years():
    result = parse_job_description(SAMPLE_JOB)
    assert result["experience_years"] == 3


def test_parse_job_extracts_education():
    result = parse_job_description(SAMPLE_JOB)
    assert result["education"] == "Bachelor's"
