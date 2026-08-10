from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """Common contract for all AI providers so swapping providers is a config change,
    not a code change."""

    @abstractmethod
    def generate_recommendations(
        self,
        resume_parsed: dict,
        job_parsed: dict,
        missing_skills: list[str],
        overall_score: float,
    ) -> dict:
        """Returns {"recommendations": [...], "ai_score": 0-10, "summary_rewrite": "..."}."""
        raise NotImplementedError

    @abstractmethod
    def rewrite_bullet_points(self, bullet_points: list[str], job_parsed: dict) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def interview_tips(self, resume_parsed: dict, job_parsed: dict) -> list[str]:
        raise NotImplementedError
