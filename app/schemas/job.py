from datetime import datetime

from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str | None = None
    raw_text: str


class JobOut(BaseModel):
    id: int
    title: str | None
    raw_text: str
    parsed_data: dict
    created_at: datetime

    class Config:
        from_attributes = True
