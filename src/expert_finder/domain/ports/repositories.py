from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable
from typing import Literal

from expert_finder.domain.models import (
    EducationRecord,
    QuestionLogEntry,
    RankingRule,
    WorkExperienceRecord,
)


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
        filter_column: str | None = None,
        filter_value: str | None = None,
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
        filter_column: str | None = None,
        filter_value: str | None = None,
        top_k: int = 10,
        min_score: float = 0.0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
        ranking: dict[str, RankingRule] | None = None,
    ) -> list[str]:
        raise NotImplementedError


class QuestionLogRepository(ABC):
    @abstractmethod
    def append(self, entry: QuestionLogEntry) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        username: str | None = None,
        limit: int = 200,
        newest_first: bool = True,
    ) -> list[QuestionLogEntry]:
        raise NotImplementedError
