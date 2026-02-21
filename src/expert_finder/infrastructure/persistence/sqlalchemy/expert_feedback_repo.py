from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Engine, Select, select
from sqlalchemy.orm import Session, sessionmaker

from expert_finder.domain.models.question_logs import ExpertFeedbackEntry
from expert_finder.domain.ports.repositories import ExpertFeedbackRepository
from expert_finder.infrastructure.persistence.sqlalchemy.base import Base
from expert_finder.infrastructure.persistence.sqlalchemy.db import build_engine, build_session_factory
from expert_finder.infrastructure.persistence.sqlalchemy.models import ExpertFeedbackRow
from expert_finder.infrastructure.persistence.sqlalchemy.schema import ensure_question_id_column


def _to_utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def _from_utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=timezone.utc)


class SqlAlchemyExpertFeedbackRepository(ExpertFeedbackRepository):
    def __init__(
        self,
        *,
        db_url: str | None = None,
        db_path: Path | None = None,
        engine: Engine | None = None,
        session_factory: sessionmaker[Session] | None = None,
        create_tables: bool = True,
    ) -> None:
        self._engine = engine or build_engine(db_url=db_url, db_path=db_path)
        self._session_factory = session_factory or build_session_factory(self._engine)
        if create_tables:
            ensure_question_id_column(self._engine)
            Base.metadata.create_all(self._engine)

    def append(self, entry: ExpertFeedbackEntry) -> None:
        row = ExpertFeedbackRow(
            created_at=_to_utc_naive(entry.created_at),
            question_id=entry.question_id,
            username=entry.username,
            expert_key=entry.expert_key,
            expert_name=entry.expert_name,
            expert_linkedin_url=entry.expert_linkedin_url,
            score=entry.score,
            note=entry.note,
        )
        with self._session_factory() as session:
            session.add(row)
            session.commit()

    def list_by_question_id(self, *, question_id: str, limit: int = 200) -> list[ExpertFeedbackEntry]:
        stmt: Select[tuple[ExpertFeedbackRow]] = (
            select(ExpertFeedbackRow)
            .where(ExpertFeedbackRow.question_id == question_id)
            .order_by(ExpertFeedbackRow.created_at.desc())
            .limit(limit)
        )
        with self._session_factory() as session:
            rows = session.execute(stmt).scalars().all()

        return [
            ExpertFeedbackEntry(
                created_at=_from_utc_naive(r.created_at),
                question_id=r.question_id,
                username=r.username,
                expert_key=r.expert_key,
                expert_name=r.expert_name,
                expert_linkedin_url=r.expert_linkedin_url,
                score=r.score,
                note=r.note,
            )
            for r in rows
        ]

