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


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("qa.html", {"request": request, "username": user})


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie("access_token")
    return {"authenticated": False}

