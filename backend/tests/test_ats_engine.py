from app.services.ats_engine import WEIGHTS, calculate_skills_score, run_full_analysis


def test_skills_score_full_match():
    score, matched, missing = calculate_skills_score(
        resume_skills=["python", "django", "sql"],
        job_required=["python", "django"],
        job_nice=["sql"],
    )
    assert score == 100.0
    assert missing == []
    assert set(matched) == {"python", "django", "sql"}


def test_skills_score_partial_match():
    score, matched, missing = calculate_skills_score(
        resume_skills=["python"],
        job_required=["python", "docker"],
        job_nice=[],
    )
    assert 0 < score < 100
    assert missing == ["docker"]


def test_skills_score_no_requirements_defaults_to_full():
    score, matched, missing = calculate_skills_score(["python"], [], [])
    assert score == 100.0
    assert missing == []


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_run_full_analysis_shape():
    resume_parsed = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+1234567890",
        "skills": ["python", "fastapi"],
        "experience": [{"title": "Backend Developer", "details": ["Built APIs"]}],
        "education": [{"title": "BSc Computer Science", "details": []}],
    }
    job_parsed = {
        "required_skills": ["python", "docker"],
        "nice_to_have": ["fastapi"],
        "experience_years": 1,
        "education": "Bachelor's",
        "keywords": ["python", "docker"],
    }

    result = run_full_analysis(resume_parsed, "Jane Doe python fastapi backend developer", job_parsed)

    assert set(result) >= {
        "skills_score", "experience_score", "education_score",
        "keywords_score", "formatting_score", "overall_score",
        "match_percentage", "matched_skills", "missing_skills",
    }
    assert 0 <= result["overall_score"] <= 100
    assert "docker" in result["missing_skills"]
