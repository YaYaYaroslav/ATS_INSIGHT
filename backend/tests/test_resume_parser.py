from app.services.resume_parser import parse_resume

SAMPLE_RESUME = """
John Smith
john.smith@example.com
+1 555 123 4567

Summary
Backend developer with 5 years of experience.

Experience
Backend Developer at Acme Corp
- Built REST APIs with Python and FastAPI
- Deployed services with Docker

Education
BSc Computer Science
University of Example

Skills
Python, FastAPI, Docker, PostgreSQL, Git
"""


def test_parse_resume_extracts_contact_info():
    result = parse_resume(SAMPLE_RESUME)
    assert result["email"] == "john.smith@example.com"
    assert result["phone"] is not None


def test_parse_resume_extracts_skills():
    result = parse_resume(SAMPLE_RESUME)
    assert "python" in result["skills"]
    assert "docker" in result["skills"]
    assert "fastapi" in result["skills"]


def test_parse_resume_extracts_experience():
    result = parse_resume(SAMPLE_RESUME)
    assert len(result["experience"]) >= 1


def test_parse_resume_handles_empty_text():
    result = parse_resume("")
    assert result["skills"] == []
    assert result["email"] is None
