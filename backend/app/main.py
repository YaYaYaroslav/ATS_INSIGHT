import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_BASE_URL,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Schema is managed by Alembic — run `alembic upgrade head` before starting.


@app.get("/")
def root():
    return {"service": settings.PROJECT_NAME, "status": "ok", "ai_provider": settings.AI_PROVIDER}


@app.get("/health")
def health():
    return {"status": "healthy"}
