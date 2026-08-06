from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
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


@router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    label: str | None = Form(None),
    parent_id: int | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Завантаження резюме (PDF/DOCX). Якщо передано parent_id — це нова
    версія вже існуючого резюме (для функції порівняння версій).
    """
    contents = await file.read()
    ext = validate_upload(file, contents)
    stored_path = save_upload(contents, ext)

    if ext == "pdf":
        raw_text = extract_text_from_pdf(stored_path)
    else:
        raw_text = extract_text_from_docx(stored_path)

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Не вдалося витягти текст з файлу. Перевір, що файл не є сканом-зображенням.")

    parsed_data = parse_resume(raw_text)

    version = 1
    if parent_id:
        parent = db.query(Resume).filter(Resume.id == parent_id, Resume.user_id == current_user.id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Батьківське резюме не знайдено")
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
        raise HTTPException(status_code=404, detail="Резюме не знайдено")
    return resume


@router.get("/{resume_id}/versions", response_model=list[ResumeVersionCompareItem])
def compare_resume_versions(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Повертає всі версії резюме (включно з коренем) разом з їхніми останніми
    ATS-скорами — це і є фіча "порівняння версій резюме" з архітектури.
    """
    root = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not root:
        raise HTTPException(status_code=404, detail="Резюме не знайдено")

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
        raise HTTPException(status_code=404, detail="Резюме не знайдено")
    db.delete(resume)
    db.commit()
