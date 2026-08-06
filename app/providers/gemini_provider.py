import json
import logging

from google import genai
from google.genai import types

from app.core.config import settings
from app.providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """
    Використовує новий уніфікований SDK `google-genai` (пакет `google.genai`),
    а не застарілий `google-generativeai`. Це важливо: ключі, які Google
    видає зараз у AI Studio, мають формат `AQ.Ab...` ("Auth key") замість
    старого `AIzaSy...` ("Standard key") — старі клієнти/SDK, заточені під
    формат AIza, можуть не приймати нові ключі. Новий SDK з такими ключами
    працює коректно.
    """

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY не задано. Додай його в .env, або встанови AI_PROVIDER=none/ollama."
            )
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    def _call_json(self, prompt: str) -> dict | list:
        """Викликає Gemini і намагається розпарсити JSON з відповіді."""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
            ),
        )
        raw = (response.text or "").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.strip("`")
            cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned
            return json.loads(cleaned)

    def generate_recommendations(
        self,
        resume_parsed: dict,
        job_parsed: dict,
        missing_skills: list[str],
        overall_score: float,
    ) -> dict:
        prompt = f"""
Ти — досвідчений career coach і ATS-експерт. Проаналізуй резюме кандидата
відносно вакансії та дай конкретні, дієві поради.

РЕЗЮМЕ (структуровані дані):
{json.dumps(resume_parsed, ensure_ascii=False, indent=2)}

ВАКАНСІЯ (структуровані дані):
{json.dumps(job_parsed, ensure_ascii=False, indent=2)}

Відсутні навички (є у вакансії, немає в резюме): {missing_skills}
Поточний ATS Score: {overall_score}/100

Поверни СТРОГО JSON у форматі (без жодного тексту навколо):
{{
  "recommendations": ["порада 1", "порада 2", "порада 3", "порада 4", "порада 5"],
  "ai_score": <число від 0 до 10, оцінка загальної відповідності резюме вакансії>,
  "summary_rewrite": "новий покращений абзац Summary для цього резюме під цю вакансію, 2-4 речення"
}}

Поради мають бути конкретними (не загальними фразами), базуватись на реальних
прогалинах між резюме і вакансією, і бути українською мовою.
"""
        try:
            result = self._call_json(prompt)
            return {
                "recommendations": result.get("recommendations", []),
                "ai_score": float(result.get("ai_score", 0)),
                "summary_rewrite": result.get("summary_rewrite"),
            }
        except Exception as exc:
            logger.exception("Gemini generate_recommendations failed: %s", exc)
            return {
                "recommendations": ["Не вдалося отримати AI-рекомендації. Спробуй ще раз пізніше."],
                "ai_score": None,
                "summary_rewrite": None,
            }

    def rewrite_bullet_points(self, bullet_points: list[str], job_parsed: dict) -> list[str]:
        prompt = f"""
Перепиши наступні bullet points резюме так, щоб вони:
- починались з дієслів дії (action verbs)
- містили вимірювані результати там, де це можливо (навіть орієнтовні)
- були релевантні до цієї вакансії: {json.dumps(job_parsed.get('keywords', []), ensure_ascii=False)}

Оригінальні bullet points:
{json.dumps(bullet_points, ensure_ascii=False, indent=2)}

Поверни СТРОГО JSON: {{"rewritten": ["...", "...", ...]}}
"""
        try:
            result = self._call_json(prompt)
            return result.get("rewritten", bullet_points)
        except Exception as exc:
            logger.exception("Gemini rewrite_bullet_points failed: %s", exc)
            return bullet_points

    def interview_tips(self, resume_parsed: dict, job_parsed: dict) -> list[str]:
        prompt = f"""
На основі цього резюме та вакансії дай 5 конкретних порад щодо підготовки
до співбесіди (технічні теми для повторення, слабкі місця в досвіді,
питання, які варто підготувати).

Резюме: {json.dumps(resume_parsed, ensure_ascii=False)}
Вакансія: {json.dumps(job_parsed, ensure_ascii=False)}

Поверни СТРОГО JSON: {{"tips": ["...", "...", "...", "...", "..."]}}
"""
        try:
            result = self._call_json(prompt)
            return result.get("tips", [])
        except Exception as exc:
            logger.exception("Gemini interview_tips failed: %s", exc)
            return []
