from __future__ import annotations

from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import NoSuchTableError


def ensure_question_id_column(engine: Engine) -> None:
    """
    Best-effort schema upgrade for existing SQLite DBs.

    This project uses SQLAlchemy's `create_all()` without a migration framework.
    Adding a new column requires an ALTER TABLE for existing databases.
    """
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    try:
        columns = {c["name"] for c in inspector.get_columns("question_logs")}
    except NoSuchTableError:
        # Fresh DB: `create_all()` will create the table with the new column.
        return
    if "question_id" in columns:
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE question_logs ADD COLUMN question_id TEXT"))
        # Unique index allows multiple NULLs in SQLite, so it won't break existing rows.
        conn.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS idx_question_logs_question_id ON question_logs(question_id)")
        )

