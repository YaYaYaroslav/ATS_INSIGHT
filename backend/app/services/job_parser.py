"""Rule-based job description parser (no AI) so matching works without an AI provider."""

import re

from app.services.resume_parser import KNOWN_SKILLS
from app.utils.text_utils import normalize, tokenize_words

NICE_TO_HAVE_MARKERS = [
    "nice to have", "nice-to-have", "preferred", "plus", "bonus", "буде плюсом", "буде перевагою",
]
REQUIRED_MARKERS = [
    "required", "requirements", "must have", "must-have", "необхідні навички", "вимоги",
]
RESPONSIBILITY_MARKERS = [
    "responsibilities", "you will", "what you'll do", "обов'язки", "завдання",
]

EXPERIENCE_RE = re.compile(r"(\d+)\+?\s*(?:years?|років|роки|рік)", re.IGNORECASE)

EDUCATION_KEYWORDS = {
    "bachelor": "Bachelor's", "bachelor's": "Bachelor's",
    "master": "Master's", "master's": "Master's",
    "phd": "PhD", "degree": "Degree",
    "бакалавр": "Bachelor's", "магістр": "Master's",
}


def _find_section(text_lower: str, markers: list[str]) -> str | None:
    for marker in markers:
        idx = text_lower.find(marker)
        if idx == -1:
            continue
        after = text_lower[idx + len(marker):]
        end = after.find("\n\n")
        return after[: end if end != -1 else 800]
    return None


def _extract_skills_from_text(text_lower: str) -> list[str]:
    found = []
    for skill in KNOWN_SKILLS:
        pattern = r"(?<![a-zA-Z0-9]){}(?![a-zA-Z0-9])".format(re.escape(skill))
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(found)


def _extract_experience_years(text: str) -> int | None:
    m = EXPERIENCE_RE.search(text)
    return int(m.group(1)) if m else None


def _extract_education(text_lower: str) -> str | None:
    for kw, label in EDUCATION_KEYWORDS.items():
        if kw in text_lower:
            return label
    return None


def _extract_responsibilities(block: str | None) -> list[str]:
    if not block:
        return []
    lines = [l.strip().lstrip("-•*– ").strip() for l in block.split("\n")]
    return [l for l in lines if l]


def parse_job_description(raw_text: str) -> dict:
    text = normalize(raw_text)
    text_lower = text.lower()

    all_skills = _extract_skills_from_text(text_lower)

    nice_block = _find_section(text_lower, NICE_TO_HAVE_MARKERS)
    nice_to_have = _extract_skills_from_text(nice_block) if nice_block else []

    required_skills = [s for s in all_skills if s not in nice_to_have]
    responsibilities_block = _find_section(text_lower, RESPONSIBILITY_MARKERS)

    return {
        "required_skills": required_skills,
        "nice_to_have": nice_to_have,
        "experience_years": _extract_experience_years(text),
        "education": _extract_education(text_lower),
        "responsibilities": _extract_responsibilities(responsibilities_block),
        "keywords": sorted(tokenize_words(text) & (KNOWN_SKILLS | set(required_skills))),
    }
