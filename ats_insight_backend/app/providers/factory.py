import logging

from app.core.config import settings
from app.providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class NoOpProvider(BaseAIProvider):
    def generate_recommendations(self, resume_parsed, job_parsed, missing_skills, overall_score) -> dict:
        return {"recommendations": [], "ai_score": None, "summary_rewrite": None}

    def rewrite_bullet_points(self, bullet_points, job_parsed) -> list[str]:
        return bullet_points

    def interview_tips(self, resume_parsed, job_parsed) -> list[str]:
        return []


_provider_instance: BaseAIProvider | None = None


def get_ai_provider() -> BaseAIProvider:
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_name = settings.AI_PROVIDER.lower()

    try:
        if provider_name == "gemini":
            from app.providers.gemini_provider import GeminiProvider
            _provider_instance = GeminiProvider()
        elif provider_name == "ollama":
            from app.providers.ollama_provider import OllamaProvider
            _provider_instance = OllamaProvider()
        else:
            _provider_instance = NoOpProvider()
    except Exception as exc:
        logger.warning("Не вдалося ініціалізувати AI провайдер '%s': %s. Використовую NoOpProvider.", provider_name, exc)
        _provider_instance = NoOpProvider()

    return _provider_instance
