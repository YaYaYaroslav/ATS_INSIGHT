import json
import logging

import httpx

from app.core.config import settings
from app.providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """Локальна альтернатива Gemini через Ollama REST API (/api/generate)."""

    def _call_json(self, prompt: str) -> dict:
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
            timeout=60,
        )
        response.raise_for_status()
        raw = response.json().get("response", "{}")
        return json.loads(raw)

    def generate_recommendations(self, resume_parsed, job_parsed, missing_skills, overall_score) -> dict:
        prompt = (
            "Проаналізуй резюме відносно вакансії і поверни JSON "
            '{"recommendations": [...], "ai_score": 0-10, "summary_rewrite": "..."}. '
            f"Резюме: {json.dumps(resume_parsed, ensure_ascii=False)}. "
            f"Вакансія: {json.dumps(job_parsed, ensure_ascii=False)}. "
            f"Відсутні навички: {missing_skills}. ATS Score: {overall_score}."
        )
        try:
            result = self._call_json(prompt)
            return {
                "recommendations": result.get("recommendations", []),
                "ai_score": float(result.get("ai_score", 0)),
                "summary_rewrite": result.get("summary_rewrite"),
            }
        except Exception as exc:
            logger.exception("Ollama generate_recommendations failed: %s", exc)
            return {"recommendations": [], "ai_score": None, "summary_rewrite": None}

    def rewrite_bullet_points(self, bullet_points, job_parsed) -> list[str]:
        prompt = (
            'Перепиши bullet points у JSON {"rewritten": [...]}: '
            f"{json.dumps(bullet_points, ensure_ascii=False)} для вакансії {json.dumps(job_parsed, ensure_ascii=False)}"
        )
        try:
            result = self._call_json(prompt)
            return result.get("rewritten", bullet_points)
        except Exception as exc:
            logger.exception("Ollama rewrite_bullet_points failed: %s", exc)
            return bullet_points

    def interview_tips(self, resume_parsed, job_parsed) -> list[str]:
        prompt = (
            'Дай 5 порад для співбесіди у JSON {"tips": [...]} для '
            f"резюме {json.dumps(resume_parsed, ensure_ascii=False)} і вакансії {json.dumps(job_parsed, ensure_ascii=False)}"
        )
        try:
            result = self._call_json(prompt)
            return result.get("tips", [])
        except Exception as exc:
            logger.exception("Ollama interview_tips failed: %s", exc)
            return []
