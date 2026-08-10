"""ATS Rule Engine + Match Calculator.

Weights: Skills 35% / Experience 25% / Education 10% / Keywords 20% / Formatting 10%
"""

from app.utils.text_utils import tokenize_words

WEIGHTS = {
    "skills": 0.35,
    "experience": 0.25,
    "education": 0.10,
    "keywords": 0.20,
    "formatting": 0.10,
}


def calculate_skills_score(
    resume_skills: list[str], job_required: list[str], job_nice: list[str]
) -> tuple[float, list[str], list[str]]:
    resume_set = {s.lower() for s in resume_skills}
    required_set = {s.lower() for s in job_required}
    nice_set = {s.lower() for s in job_nice}

    if not required_set and not nice_set:
        return 100.0, sorted(resume_set), []

    matched_required = resume_set & required_set
    missing_required = required_set - resume_set
    matched_nice = resume_set & nice_set

    required_ratio = (len(matched_required) / len(required_set)) if required_set else 1.0
    nice_ratio = (len(matched_nice) / len(nice_set)) if nice_set else 1.0

    score = (required_ratio * 0.8 + nice_ratio * 0.2) * 100
    matched = sorted(matched_required | matched_nice)
    missing = sorted(missing_required)

    return round(score, 1), matched, missing


def calculate_experience_score(resume_experience: list[dict], job_required_years: int | None) -> float:
    if job_required_years is None:
        return 80.0 if resume_experience else 40.0

    estimated_years = max(len(resume_experience) * 1.5, 0)
    if estimated_years >= job_required_years:
        return 100.0
    if estimated_years == 0:
        return 20.0
    return round((estimated_years / job_required_years) * 100, 1)


def calculate_education_score(resume_education: list[dict], job_education: str | None) -> float:
    if not job_education:
        return 100.0 if resume_education else 60.0
    if not resume_education:
        return 30.0

    combined = " ".join(
        (item.get("title", "") + " " + " ".join(item.get("details", []))) for item in resume_education
    ).lower()

    if job_education.lower().split("'")[0] in combined:
        return 100.0
    return 60.0 if resume_education else 30.0


def calculate_keywords_score(resume_raw_text: str, job_keywords: list[str]) -> float:
    if not job_keywords:
        return 100.0
    resume_tokens = tokenize_words(resume_raw_text)
    job_tokens = {k.lower() for k in job_keywords}
    matched = resume_tokens & job_tokens
    return round((len(matched) / len(job_tokens)) * 100, 1) if job_tokens else 100.0


def calculate_formatting_score(resume_parsed: dict) -> float:
    checks = [
        bool(resume_parsed.get("name")),
        bool(resume_parsed.get("email")),
        bool(resume_parsed.get("phone")),
        bool(resume_parsed.get("skills")),
        bool(resume_parsed.get("experience")),
    ]
    return round((sum(checks) / len(checks)) * 100, 1)


def calculate_overall_score(scores: dict[str, float]) -> float:
    total = sum(scores[key] * WEIGHTS[key] for key in WEIGHTS)
    return round(total, 1)


def calculate_match_percentage(matched_skills: list[str], job_required: list[str], job_nice: list[str]) -> float:
    total_job_skills = set(s.lower() for s in job_required) | set(s.lower() for s in job_nice)
    if not total_job_skills:
        return 100.0
    return round((len(set(matched_skills) & total_job_skills) / len(total_job_skills)) * 100, 1)


def run_full_analysis(resume_parsed: dict, resume_raw_text: str, job_parsed: dict) -> dict:
    skills_score, matched_skills, missing_skills = calculate_skills_score(
        resume_parsed.get("skills", []),
        job_parsed.get("required_skills", []),
        job_parsed.get("nice_to_have", []),
    )
    experience_score = calculate_experience_score(
        resume_parsed.get("experience", []), job_parsed.get("experience_years")
    )
    education_score = calculate_education_score(resume_parsed.get("education", []), job_parsed.get("education"))
    keywords_score = calculate_keywords_score(resume_raw_text, job_parsed.get("keywords", []))
    formatting_score = calculate_formatting_score(resume_parsed)

    scores = {
        "skills": skills_score,
        "experience": experience_score,
        "education": education_score,
        "keywords": keywords_score,
        "formatting": formatting_score,
    }
    overall = calculate_overall_score(scores)
    match_percentage = calculate_match_percentage(
        matched_skills, job_parsed.get("required_skills", []), job_parsed.get("nice_to_have", [])
    )

    return {
        "skills_score": skills_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "keywords_score": keywords_score,
        "formatting_score": formatting_score,
        "overall_score": overall,
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
