import json
import logging

from google import genai
from google.genai import types

from app.core.config import settings
from app.providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Uses the unified `google-genai` SDK, required for the current "AQ.Ab..." API key
    format — the older `google-generativeai` SDK does not support it."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to .env, or set AI_PROVIDER=none/ollama.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    def _call_json(self, prompt: str) -> dict | list:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4, response_mime_type="application/json"),
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
You are an experienced career coach and ATS expert. Analyze the candidate's
resume against the job and give concrete, actionable advice.

RESUME (structured data):
{json.dumps(resume_parsed, ensure_ascii=False, indent=2)}

JOB (structured data):
{json.dumps(job_parsed, ensure_ascii=False, indent=2)}

Missing skills (present in the job, absent from the resume): {missing_skills}
Current ATS Score: {overall_score}/100

Return STRICT JSON in this format (no surrounding text):
{{
  "recommendations": ["tip 1", "tip 2", "tip 3", "tip 4", "tip 5"],
  "ai_score": <number 0-10, overall resume-to-job fit>,
  "summary_rewrite": "a new, improved Summary paragraph for this resume tailored to this job, 2-4 sentences"
}}

Recommendations must be specific (not generic phrases), based on real gaps
between the resume and the job.
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
                "recommendations": ["Could not get AI recommendations. Please try again later."],
                "ai_score": None,
                "summary_rewrite": None,
            }

    def rewrite_bullet_points(self, bullet_points: list[str], job_parsed: dict) -> list[str]:
        prompt = f"""
Rewrite the following resume bullet points so they:
- start with action verbs
- include measurable results where possible (even approximate)
- are relevant to this job: {json.dumps(job_parsed.get('keywords', []), ensure_ascii=False)}

Original bullet points:
{json.dumps(bullet_points, ensure_ascii=False, indent=2)}

Return STRICT JSON: {{"rewritten": ["...", "...", ...]}}
"""
        try:
            result = self._call_json(prompt)
            return result.get("rewritten", bullet_points)
        except Exception as exc:
            logger.exception("Gemini rewrite_bullet_points failed: %s", exc)
            return bullet_points

    def interview_tips(self, resume_parsed: dict, job_parsed: dict) -> list[str]:
        prompt = f"""
Based on this resume and job, give 5 concrete interview-preparation tips
(technical topics to review, weak spots in experience, questions to prepare for).

Resume: {json.dumps(resume_parsed, ensure_ascii=False)}
Job: {json.dumps(job_parsed, ensure_ascii=False)}

Return STRICT JSON: {{"tips": ["...", "...", "...", "...", "..."]}}
"""
        try:
            result = self._call_json(prompt)
            return result.get("tips", [])
        except Exception as exc:
            logger.exception("Gemini interview_tips failed: %s", exc)
            return []
