from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobOut
from app.services.job_parser import parse_job_description

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    parsed_data = parse_job_description(payload.raw_text)

    job = Job(
        user_id=current_user.id,
        title=payload.title,
        raw_text=payload.raw_text,
        parsed_data=parsed_data,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.user_id == current_user.id).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Вакансію не знайдено")
    return job
