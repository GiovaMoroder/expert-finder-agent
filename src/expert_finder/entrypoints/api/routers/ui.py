"""UI routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from expert_finder.entrypoints.api.deps import current_user


_api_base_dir = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(_api_base_dir / "templates"))

router = APIRouter(tags=["ui"])

def _static_version() -> str:
    static_dir = _api_base_dir / "static"
    candidates = [
        static_dir / "app.css",
        static_dir / "qa.js",
        static_dir / "login.js",
    ]
    latest_ns = 0
    for p in candidates:
        try:
            latest_ns = max(latest_ns, p.stat().st_mtime_ns)
        except FileNotFoundError:
            continue
    return str(latest_ns or 1)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "static_version": _static_version()},
    )


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "qa.html",
        {"request": request, "username": user, "static_version": _static_version()},
    )


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie("access_token")
    return {"authenticated": False}

