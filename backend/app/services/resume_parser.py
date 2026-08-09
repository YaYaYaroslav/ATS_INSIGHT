import re

from app.utils.text_utils import normalize, extract_email, extract_phone


KNOWN_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby", "kotlin", "swift",
    "django", "flask", "fastapi", "spring", "spring boot", "react", "vue", "angular", "next.js", "node.js",
    "express", "nestjs", ".net", "asp.net",
    "sql", "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "elasticsearch", "cassandra",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible", "jenkins", "ci/cd", "git", "github",
    "gitlab", "linux", "nginx", "rabbitmq", "kafka", "graphql", "rest", "grpc", "microservices",
    "html", "css", "sass", "tailwind", "bootstrap", "webpack", "vite",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv", "nlp",
    "machine learning", "deep learning", "data analysis", "data science", "power bi", "tableau", "excel",
    "agile", "scrum", "jira", "confluence", "figma", "photoshop",
    "unit testing", "pytest", "selenium", "cypress", "junit",
}

SECTION_HEADERS = {
    "experience": [
        "experience", "work experience", "employment history", "professional experience",
        "досвід роботи", "досвід", "трудова діяльність",
    ],
    "education": [
        "education", "academic background", "освіта",
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "навички", "технічні навички",
    ],
    "projects": [
        "projects", "personal projects", "проєкти", "проекти",
    ],
    "languages": [
        "languages", "мови",
    ],
    "certificates": [
        "certificates", "certifications", "сертифікати",
    ],
    "summary": [
        "summary", "profile", "about", "objective", "про себе",
    ],
}


def _split_into_sections(text: str) -> dict[str, str]:
    lines = text.split("\n")
    header_to_key = {}
    for key, variants in SECTION_HEADERS.items():
        for v in variants:
            header_to_key[v] = key

    sections: dict[str, list[str]] = {"header": []}
    current = "header"

    for line in lines:
        stripped = line.strip().lower().strip(":").strip()
        matched_key = None
        if 0 < len(stripped) <= 40 and stripped in header_to_key:
            matched_key = header_to_key[stripped]

        if matched_key:
            current = matched_key
            sections.setdefault(current, [])
            continue

        sections.setdefault(current, [])
        sections[current].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _extract_skills(full_text_lower: str) -> list[str]:
    found = []
    for skill in KNOWN_SKILLS:
        pattern = r"(?<![a-zA-Z0-9]){}(?![a-zA-Z0-9])".format(re.escape(skill))
        if re.search(pattern, full_text_lower):
            found.append(skill)
    return sorted(found)


def _extract_name(header_block: str) -> str | None:
    for line in header_block.split("\n"):
        line = line.strip()
        if not line or "@" in line or any(ch.isdigit() for ch in line):
            continue
        if 2 <= len(line.split()) <= 5:
            return line
    return None


def _extract_location(header_block: str) -> str | None:
    for line in header_block.split("\n")[:10]:
        line = line.strip()
        if "," in line and 2 < len(line) < 60 and not any(ch.isdigit() for ch in line) and "@" not in line:
            return line
    return None


def _extract_bullet_items(block: str) -> list[dict]:
    items: list[dict] = []
    current_title = None
    current_bullets: list[str] = []

    def flush():
        if current_title:
            items.append({"title": current_title, "details": current_bullets})

    for line in block.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        is_bullet = stripped.startswith(("-", "•", "*", "–"))
        if is_bullet:
            current_bullets.append(stripped.lstrip("-•*– ").strip())
        else:
            flush()
            current_title = stripped
            current_bullets = []
    flush()
    return items


def _extract_languages(block: str) -> list[str]:
    if not block:
        return []
    raw = re.split(r"[,\n;]", block)
    return [r.strip() for r in raw if r.strip()]


def parse_resume(raw_text: str) -> dict:
    text = normalize(raw_text)
    text_lower = text.lower()
    sections = _split_into_sections(text)

    header_block = sections.get("header", "")

    parsed = {
        "name": _extract_name(header_block),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": _extract_location(header_block),
        "skills": _extract_skills(text_lower),
        "education": _extract_bullet_items(sections.get("education", "")),
        "experience": _extract_bullet_items(sections.get("experience", "")),
        "projects": _extract_bullet_items(sections.get("projects", "")),
        "languages": _extract_languages(sections.get("languages", "")),
        "certificates": _extract_languages(sections.get("certificates", "")),
        "summary": sections.get("summary", "") or None,
    }
    return parsed
