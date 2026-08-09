from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    @abstractmethod
    def generate_recommendations(
        self,
        resume_parsed: dict,
        job_parsed: dict,
        missing_skills: list[str],
        overall_score: float,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    def rewrite_bullet_points(self, bullet_points: list[str], job_parsed: dict) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def interview_tips(self, resume_parsed: dict, job_parsed: dict) -> list[str]:
        raise NotImplementedError
