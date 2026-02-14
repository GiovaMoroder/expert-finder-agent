from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable
from typing import Literal

from expert_finder.domain.models import EducationRecord, RankingRule, WorkExperienceRecord


class WorkExperienceRepository(ABC):
    @abstractmethod
    def list_all(self) -> Iterable[WorkExperienceRecord]:
        raise NotImplementedError

    @abstractmethod
    def find_by_company(self, company: str) -> list[WorkExperienceRecord]:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        filter_column: str,
        filter_value: str,
        top_k: int = 10,
        min_score: float = 0.0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
        ranking: dict[str, RankingRule] | None = None,
    ) -> list[str]:
        raise NotImplementedError


class EducationRepository(ABC):
    @abstractmethod
    def list_all(self) -> Iterable[EducationRecord]:
        raise NotImplementedError

    @abstractmethod
    def find_by_institution(self, institution: str) -> list[EducationRecord]:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        filter_column: str,
        filter_value: str,
        top_k: int = 10,
        min_score: float = 0.0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
        ranking: dict[str, RankingRule] | None = None,
    ) -> list[str]:
        raise NotImplementedError
