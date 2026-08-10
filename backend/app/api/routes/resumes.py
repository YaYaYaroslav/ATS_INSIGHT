import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeOut, ResumeVersionCompareItem
from app.services.docx_extractor import extract_text_from_docx
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.resume_parser import parse_resume
from app.utils.file_utils import validate_upload, save_upload

router = APIRouter(prefix="/resumes", tags=["Resumes"])

FILE_MEDIA_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    label: str | None = Form(None),
    parent_id: int | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """If parent_id is given, this upload is a new version of an existing resume
    (used for version comparison)."""
    contents = await file.read()
    ext = validate_upload(file, contents)
    stored_path = save_upload(contents, ext)

    raw_text = extract_text_from_pdf(stored_path) if ext == "pdf" else extract_text_from_docx(stored_path)

    if not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from the file. Make sure it isn't a scanned image.",
        )

    parsed_data = parse_resume(raw_text)

    version = 1
    if parent_id:
        parent = db.query(Resume).filter(Resume.id == parent_id, Resume.user_id == current_user.id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent resume not found")
        sibling_count = db.query(Resume).filter(
            (Resume.parent_id == parent_id) | (Resume.id == parent_id)
        ).count()
        version = sibling_count + 1

    resume = Resume(
        user_id=current_user.id,
        parent_id=parent_id,
        version=version,
        label=label or (f"Resume v{version}" if parent_id else "Resume v1"),
        original_filename=file.filename,
        stored_path=stored_path,
        file_type=ext,
        raw_text=raw_text,
        parsed_data=parsed_data,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeOut])
def list_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.get("/{resume_id}/file")
def get_resume_file(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Serves the original resume file (PDF opens inline, DOCX downloads)."""
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not os.path.exists(resume.stored_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        resume.stored_path,
        media_type=FILE_MEDIA_TYPES.get(resume.file_type, "application/octet-stream"),
        filename=resume.original_filename,
        content_disposition_type="inline" if resume.file_type == "pdf" else "attachment",
    )


@router.get("/{resume_id}/versions", response_model=list[ResumeVersionCompareItem])
def compare_resume_versions(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns all versions of a resume (including the root) with their latest ATS scores."""
    root = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not root:
        raise HTTPException(status_code=404, detail="Resume not found")

    root_id = root.parent_id or root.id
    versions = db.query(Resume).filter(
        ((Resume.id == root_id) | (Resume.parent_id == root_id)),
        Resume.user_id == current_user.id,
    ).order_by(Resume.version.asc()).all()

    result = []
    for v in versions:
        latest_analysis = (
            db.query(Analysis)
            .filter(Analysis.resume_id == v.id)
            .order_by(Analysis.created_at.desc())
            .first()
        )
        result.append(
            ResumeVersionCompareItem(
                resume_id=v.id,
                label=v.label,
                version=v.version,
                ats_score=latest_analysis.overall_score if latest_analysis else None,
                match_percentage=latest_analysis.match_percentage if latest_analysis else None,
                ai_score=latest_analysis.ai_score if latest_analysis else None,
                created_at=v.created_at,
            )
        )
    return result


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()
