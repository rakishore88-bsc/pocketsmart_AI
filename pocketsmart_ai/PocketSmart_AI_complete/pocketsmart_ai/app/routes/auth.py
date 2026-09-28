from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.auth import create_access_token, hash_password, verify_password
from app.database import create_user, get_user_by_email
from app.models.schemas import LoginRequest, RegisterRequest

router = APIRouter()


def _wants_json(request: Request) -> bool:
    return "application/json" in request.headers.get("accept", "")


@router.post("/register")
async def register(request: Request):
    if _wants_json(request):
        data = RegisterRequest.model_validate(await request.json())
    else:
        form = await request.form()
        data = RegisterRequest(name=str(form.get("name", "")), email=str(form.get("email", "")), password=str(form.get("password", "")))
    if get_user_by_email(data.email):
        raise HTTPException(409, "An account with this email already exists")
    user = create_user(data.email, data.name, hash_password(data.password))
    if _wants_json(request):
        token = create_access_token(user["id"])
        return {"message": "Registration successful", "user": user, "access_token": token}
    return RedirectResponse("/login?registered=1", status_code=303)


@router.post("/login")
async def login(request: Request):
    if _wants_json(request):
        data = LoginRequest.model_validate(await request.json())
    else:
        form = await request.form()
        data = LoginRequest(email=str(form.get("email", "")), password=str(form.get("password", "")))
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        if _wants_json(request):
            raise HTTPException(401, "Invalid email or password")
        return RedirectResponse("/login?error=1", status_code=303)
    token = create_access_token(user["id"])
    if _wants_json(request):
        return {"message": "Login successful", "user": {"id": user["id"], "email": user["email"], "name": user["name"]}, "access_token": token}
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=60*60*24)
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.post("/token")
async def token(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_access_token(user["id"]), "token_type": "bearer"}
