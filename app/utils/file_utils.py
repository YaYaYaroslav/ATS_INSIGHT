import os
import uuid

from fastapi import UploadFile, HTTPException, status

from app.core.config import settings


def validate_upload(file: UploadFile, contents: bytes) -> str:
    """Перевіряє розширення та розмір файлу. Повертає нормалізоване розширення ('pdf'|'docx')."""
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Непідтримуваний формат файлу: {ext}. Дозволено: {settings.ALLOWED_EXTENSIONS}",
        )

    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл занадто великий: {size_mb:.2f}MB (максимум {settings.MAX_UPLOAD_SIZE_MB}MB)",
        )

    return ext.lstrip(".")


def save_upload(contents: bytes, ext: str) -> str:
    """Зберігає файл на диск під унікальним ім'ям, повертає шлях."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(settings.UPLOAD_DIR, unique_name)
    with open(path, "wb") as f:
        f.write(contents)
    return path
