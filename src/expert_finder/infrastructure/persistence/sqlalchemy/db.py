from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def _default_db_path() -> Path:
    # Local/dev default. Can be overridden with EXPERT_FINDER_DB_PATH.
    return Path(os.environ.get("EXPERT_FINDER_DB_PATH", "./data/expert_finder.sqlite3"))


def build_engine(*, db_url: str | None = None, db_path: Path | None = None) -> Engine:
    if db_url is None:
        path = db_path or _default_db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        db_url = f"sqlite+pysqlite:///{path}"

    engine_kwargs: dict = {"pool_pre_ping": True}
    if db_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(db_url, **engine_kwargs)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
