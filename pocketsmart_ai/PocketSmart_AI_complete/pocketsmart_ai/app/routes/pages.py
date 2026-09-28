from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth import get_current_user_optional
from app.database import get_history

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def ctx(request: Request, **extra):
    return {"request": request, "user": get_current_user_optional(request), **extra}


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", ctx(request))


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", ctx(request))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", ctx(request))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user_optional(request)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/login", status_code=303)
    history = get_history(user["id"], 6)
    return templates.TemplateResponse("dashboard.html", ctx(request, history=history))


@router.get("/home-planner", response_class=HTMLResponse)
async def home_planner(request: Request):
    return templates.TemplateResponse("home_planner.html", ctx(request))


@router.get("/party-planner", response_class=HTMLResponse)
async def party_planner(request: Request):
    return templates.TemplateResponse("party_planner.html", ctx(request))


@router.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner(request: Request):
    return templates.TemplateResponse("jewelry_planner.html", ctx(request))


@router.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    user = get_current_user_optional(request)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("history.html", ctx(request, history=get_history(user["id"], 50)))
