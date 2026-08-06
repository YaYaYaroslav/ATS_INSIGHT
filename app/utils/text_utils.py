import re


def normalize(text: str) -> str:
    """Нижній регістр, прибирає зайві пробіли/переноси."""
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize_words(text: str) -> set[str]:
    """Повертає множину нормалізованих слів/токенів (lowercase, без пунктуації)."""
    words = re.findall(r"[a-zA-Zа-яіїєА-ЯІЇЄ0-9\+\#\.\-]{2,}", text.lower())
    return {w.strip(".-") for w in words if w.strip(".-")}


EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}")


def extract_email(text: str) -> str | None:
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None


def extract_phone(text: str) -> str | None:
    for m in PHONE_RE.finditer(text):
        candidate = m.group(0).strip()
        digits = re.sub(r"\D", "", candidate)
        if 7 <= len(digits) <= 15:
            return candidate
    return None
