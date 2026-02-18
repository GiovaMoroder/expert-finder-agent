"""FastAPI entrypoint for Expert Finder."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from expert_finder.entrypoints.api.deps import get_agent
from expert_finder.entrypoints.api.routers import auth, qa, ui
from expert_finder.infrastructure.logging import setup_logging, silence_third_party_loggers


def _api_base_dir() -> Path:
    return Path(__file__).resolve().parent


def create_app() -> FastAPI:
    load_dotenv()
    setup_logging(os.environ.get("LOG_LEVEL", "INFO"))
    silence_third_party_loggers()

    app = FastAPI(title="Expert Finder API")

    base_dir = _api_base_dir()
    app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")

    app.include_router(auth.router)
    app.include_router(ui.router)
    app.include_router(qa.router)
    return app


app = create_app()
