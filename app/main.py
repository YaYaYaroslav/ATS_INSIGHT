import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.models import user, resume, job, analysis  # noqa: F401 — реєструє моделі в Base.metadata

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # у продакшні звузити до домену фронтенду
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup():
    # Для MVP створюємо таблиці напряму. У продакшні перейти на Alembic-міграції.
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"service": settings.PROJECT_NAME, "status": "ok", "ai_provider": settings.AI_PROVIDER}


@app.get("/health")
def health():
    return {"status": "healthy"}
