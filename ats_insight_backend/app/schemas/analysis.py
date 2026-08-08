from datetime import datetime

from pydantic import BaseModel


class AnalysisCreate(BaseModel):
    resume_id: int
    job_id: int
    use_ai: bool = True


class AnalysisOut(BaseModel):
    id: int
    resume_id: int
    job_id: int

    skills_score: float
    experience_score: float
    education_score: float
    keywords_score: float
    formatting_score: float
    overall_score: float

    match_percentage: float
    matched_skills: list[str]
    missing_skills: list[str]

    ai_recommendations: list[str]
    ai_score: float | None
    ai_summary_rewrite: str | None

    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisHistoryItem(BaseModel):
    id: int
    resume_id: int
    job_id: int
    overall_score: float
    match_percentage: float
    created_at: datetime

    class Config:
        from_attributes = True
