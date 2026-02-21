from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from expert_finder.infrastructure.persistence.sqlalchemy.base import Base


class QuestionLogRow(Base):
    __tablename__ = "question_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Stable identifier for linking feedback to a specific /api/ask run.
    question_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class ExpertFeedbackRow(Base):
    __tablename__ = "expert_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("question_logs.question_id"),
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    expert_key: Mapped[str] = mapped_column(String(128), nullable=False)
    expert_name: Mapped[str] = mapped_column(String(256), nullable=False)
    expert_linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


Index("idx_question_logs_username_created_at", QuestionLogRow.username, QuestionLogRow.created_at)
Index("idx_question_logs_question_id", QuestionLogRow.question_id, unique=True)
Index("idx_expert_feedback_question_id_created_at", ExpertFeedbackRow.question_id, ExpertFeedbackRow.created_at)

