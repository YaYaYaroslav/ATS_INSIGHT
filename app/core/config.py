from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Централізована конфігурація застосунку.
    Всі значення читаються зі змінних середовища / .env файлу.
    """

    # --- Загальне ---
    PROJECT_NAME: str = "ATS Insight"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # --- База даних ---
    # За замовчуванням SQLite для швидкого локального старту.
    # Для продакшну постав, наприклад:
    # postgresql+psycopg2://user:password@localhost:5432/ats_insight
    DATABASE_URL: str = "sqlite:///./ats_insight.db"

    # --- Auth / JWT ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 години

    # --- Файли ---
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: tuple = (".pdf", ".docx")

    # --- AI Provider ---
    # "gemini" | "ollama" | "none"
    AI_PROVIDER: str = "gemini"

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.6-flash"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
