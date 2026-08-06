import fitz  # PyMuPDF


def extract_text_from_pdf(path: str) -> str:
    """Витягує весь текст з PDF, зберігаючи порядок сторінок."""
    text_parts = []
    with fitz.open(path) as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts)
