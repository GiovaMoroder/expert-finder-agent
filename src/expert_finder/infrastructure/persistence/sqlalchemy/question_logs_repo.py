from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Engine, Select, select
from sqlalchemy.orm import Session, sessionmaker

from expert_finder.domain.models.question_logs import QuestionLogEntry
from expert_finder.domain.ports.repositories import QuestionLogRepository
from expert_finder.infrastructure.persistence.sqlalchemy.base import Base
from expert_finder.infrastructure.persistence.sqlalchemy.db import build_engine, build_session_factory
from expert_finder.infrastructure.persistence.sqlalchemy.models import QuestionLogRow


def _to_utc_naive(dt: datetime) -> datetime:
    """
    SQLite doesn't preserve tzinfo reliably for datetimes.
    We store all timestamps as naive UTC in the DB.
    """
    if dt.tzinfo is None:
        # Treat naive datetimes as UTC.
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def _from_utc_naive(dt: datetime) -> datetime:
    # Rows return naive datetimes -> interpret as UTC.
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=timezone.utc)


class SqlAlchemyQuestionLogRepository(QuestionLogRepository):
    def __init__(
        self,
        *,
        db_path: Path | None = None,
        engine: Engine | None = None,
        session_factory: sessionmaker[Session] | None = None,
        create_tables: bool = True,
    ) -> None:
        self._engine = engine or build_engine(db_path)
        self._session_factory = session_factory or build_session_factory(self._engine)
        if create_tables:
            Base.metadata.create_all(self._engine)

    def append(self, entry: QuestionLogEntry) -> None:
        row = QuestionLogRow(
            created_at=_to_utc_naive(entry.created_at),
            username=entry.username,
            question=entry.question,
            status=entry.status,
            latency_ms=entry.latency_ms,
            error_message=entry.error_message,
        )
        with self._session_factory() as session:
            session.add(row)
            session.commit()

    def list(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        username: str | None = None,
        limit: int = 200,
        newest_first: bool = True,
    ) -> list[QuestionLogEntry]:
        stmt: Select[tuple[QuestionLogRow]] = select(QuestionLogRow)

        if since is not None:
            stmt = stmt.where(QuestionLogRow.created_at >= _to_utc_naive(since))
        if until is not None:
            stmt = stmt.where(QuestionLogRow.created_at <= _to_utc_naive(until))
        if username is not None:
            stmt = stmt.where(QuestionLogRow.username == username)

        order_col = QuestionLogRow.created_at.desc() if newest_first else QuestionLogRow.created_at.asc()
        stmt = stmt.order_by(order_col).limit(limit)

        with self._session_factory() as session:
            rows = session.execute(stmt).scalars().all()

        return [
            QuestionLogEntry(
                created_at=_from_utc_naive(r.created_at),
                username=r.username,
                question=r.question,
                status=r.status,  # type: ignore[arg-type]
                latency_ms=r.latency_ms,
                error_message=r.error_message,
            )
            for r in rows
        ]

