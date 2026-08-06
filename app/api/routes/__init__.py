from fastapi import APIRouter

from app.api.routes import auth, resumes, jobs, analyses

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(resumes.router)
api_router.include_router(jobs.router)
api_router.include_router(analyses.router)
