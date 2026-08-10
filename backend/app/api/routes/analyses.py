from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.analysis import Analysis
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.providers.factory import get_ai_provider
from app.schemas.analysis import AnalysisCreate, AnalysisOut, AnalysisHistoryItem
from app.services.ats_engine import run_full_analysis

router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.post("", response_model=AnalysisOut, status_code=201)
def create_analysis(payload: AnalysisCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = db.query(Job).filter(Job.id == payload.job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Rule-based ATS scoring always runs, even without an AI provider.
    scores = run_full_analysis(resume.parsed_data, resume.raw_text, job.parsed_data)

    ai_recommendations, ai_score, ai_summary_rewrite = [], None, None
    if payload.use_ai:
        provider = get_ai_provider()
        ai_result = provider.generate_recommendations(
            resume_parsed=resume.parsed_data,
            job_parsed=job.parsed_data,
            missing_skills=scores["missing_skills"],
            overall_score=scores["overall_score"],
        )
        ai_recommendations = ai_result.get("recommendations", [])
        ai_score = ai_result.get("ai_score")
        ai_summary_rewrite = ai_result.get("summary_rewrite")

    analysis = Analysis(
        user_id=current_user.id,
        resume_id=resume.id,
        job_id=job.id,
        skills_score=scores["skills_score"],
        experience_score=scores["experience_score"],
        education_score=scores["education_score"],
        keywords_score=scores["keywords_score"],
        formatting_score=scores["formatting_score"],
        overall_score=scores["overall_score"],
        match_percentage=scores["match_percentage"],
        matched_skills=scores["matched_skills"],
        missing_skills=scores["missing_skills"],
        ai_recommendations=ai_recommendations,
        ai_score=ai_score,
        ai_summary_rewrite=ai_summary_rewrite,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("", response_model=list[AnalysisHistoryItem])
def list_analyses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.get("/{analysis_id}/interview-tips")
def get_interview_tips(analysis_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
    job = db.query(Job).filter(Job.id == analysis.job_id).first()

    provider = get_ai_provider()
    tips = provider.interview_tips(resume.parsed_data, job.parsed_data)
    return {"tips": tips}
