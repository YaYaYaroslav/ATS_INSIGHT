from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, JSON, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Resume(Base):
    """
    Резюме користувача. Підтримує версіонування: одне й те саме резюме
    може мати кілька версій (v1, v2, v3...), пов'язаних через parent_id.
    Це основа для функції "порівняння версій резюме".
    """

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # --- Версіонування ---
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)  # напр. "Resume v2"

    original_filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(10))  # "pdf" | "docx"

    raw_text: Mapped[str] = mapped_column(Text)
    parsed_data: Mapped[dict] = mapped_column(JSON, default=dict)
    # parsed_data приклад:
    # {
    #   "name": "...", "email": "...", "phone": "...", "location": "...",
    #   "skills": [...], "education": [...], "experience": [...],
    #   "projects": [...], "languages": [...], "certificates": [...]
    # }

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")
    children = relationship("Resume", backref="parent", remote_side=[id])
