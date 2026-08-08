from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobOut, JobFromUrl
from app.services.job_parser import parse_job_description
from app.services.job_scraper import scrape_job_posting, ScraperError

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


@router.post("/from-url", response_model=JobOut, status_code=201)
def create_job_from_url(payload: JobFromUrl, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Приймає посилання на вакансію (robota.ua, work.ua, або будь-який інший
    сайт — через generic fallback), сам витягує текст опису і одразу парсить
    його в structured job data — не треба копіювати текст вручну.
    """
    try:
        scraped = scrape_job_posting(payload.url)
    except ScraperError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    parsed_data = parse_job_description(scraped["raw_text"])

    job = Job(
        user_id=current_user.id,
        title=scraped.get("title"),
        raw_text=scraped["raw_text"],
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


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Вакансію не знайдено")
    db.delete(job)
    db.commit()
