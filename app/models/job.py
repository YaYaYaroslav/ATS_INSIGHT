from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)

    parsed_data: Mapped[dict] = mapped_column(JSON, default=dict)
    # parsed_data приклад:
    # {
    #   "required_skills": [...], "nice_to_have": [...],
    #   "experience_years": 3, "education": "Bachelor's",
    #   "responsibilities": [...], "keywords": [...]
    # }

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="jobs")
    analyses = relationship("Analysis", back_populates="job", cascade="all, delete-orphan")
