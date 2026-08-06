from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """
    Спільний контракт для всіх AI-провайдерів (Gemini, Ollama, ...).
    Завдяки цьому інтерфейсу заміна провайдера — це зміна одного
    значення AI_PROVIDER в .env, без правок у бізнес-логіці.
    """

    @abstractmethod
    def generate_recommendations(
        self,
        resume_parsed: dict,
        job_parsed: dict,
        missing_skills: list[str],
        overall_score: float,
    ) -> dict:
        """
        Повертає dict:
        {
            "recommendations": ["...", "...", ...],
            "ai_score": 8.4,          # 0-10
            "summary_rewrite": "...", # новий Summary параграф
        }
        """
        raise NotImplementedError

    @abstractmethod
    def rewrite_bullet_points(self, bullet_points: list[str], job_parsed: dict) -> list[str]:
        """Переписує список bullet points резюме під конкретну вакансію."""
        raise NotImplementedError

    @abstractmethod
    def interview_tips(self, resume_parsed: dict, job_parsed: dict) -> list[str]:
        """Генерує поради щодо проходження співбесіди на цю вакансію."""
        raise NotImplementedError
