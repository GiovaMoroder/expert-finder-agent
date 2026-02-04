from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from expert_finder.expert_finder.db.models import EducationRecord, WorkExperienceRecord


class WorkExperienceRepository(ABC):
    @abstractmethod
    def list_all(self) -> Iterable[WorkExperienceRecord]:
        raise NotImplementedError

    @abstractmethod
    def find_by_company(self, company: str) -> list[WorkExperienceRecord]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, top_k: int = 10, min_score: float = 0.0) -> list[str]:
        raise NotImplementedError


class EducationRepository(ABC):
    @abstractmethod
    def list_all(self) -> Iterable[EducationRecord]:
        raise NotImplementedError

    @abstractmethod
    def find_by_institution(self, institution: str) -> list[EducationRecord]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, top_k: int = 10, min_score: float = 0.0) -> list[str]:
        raise NotImplementedError
