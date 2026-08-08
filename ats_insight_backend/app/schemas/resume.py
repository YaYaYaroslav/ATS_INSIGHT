from datetime import datetime

from pydantic import BaseModel


class ParsedResumeData(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    skills: list[str] = []
    education: list[dict] = []
    experience: list[dict] = []
    projects: list[dict] = []
    languages: list[str] = []
    certificates: list[str] = []


class ResumeOut(BaseModel):
    id: int
    original_filename: str
    file_type: str
    version: int
    label: str | None
    parent_id: int | None
    parsed_data: dict
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeVersionCompareItem(BaseModel):
    resume_id: int
    label: str | None
    version: int
    ats_score: float | None
    match_percentage: float | None
    ai_score: float | None
    created_at: datetime
