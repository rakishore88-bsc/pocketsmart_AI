from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    JSONResponse,
    RedirectResponse,
)

from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    hash_password,
    optional_user,
    verify_password,
)

from app.database import get_db

from app.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# REGISTER
# =========================================================

@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Register a new PocketSmart AI user.
    """

    username = username.strip()
    email = email.strip().lower()

    # -------------------------
    # Validate username
    # -------------------------

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 3 characters.",
        )

    # -------------------------
    # Validate password
    # -------------------------

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters.",
        )

    # -------------------------
    # Check existing user
    # -------------------------

    existing_user = (
        db.query(User)
        .filter(
            (User.username == username)
            | (User.email == email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists.",
        )

    # -------------------------
    # Create user
    # -------------------------

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # -------------------------
    # Browser request
    # -------------------------

    accept = request.headers.get(
        "accept",
        ""
    )

    if "text/html" in accept:

        return RedirectResponse(
            url="/login?registered=1",
            status_code=303,
        )

    # -------------------------
    # API request
    # -------------------------

    return {
        "message": "Registration successful.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Authenticate an existing user.

    A JWT access token is stored in an HttpOnly cookie.
    """

    email = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not verify_password(
        password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    # -------------------------
    # Create JWT
    # -------------------------

    access_token = create_access_token(
        user.id
    )

    # -------------------------
    # Browser request
    # -------------------------

    accept = request.headers.get(
        "accept",
        ""
    )

    if "text/html" in accept:

        response = RedirectResponse(
            url="/dashboard",
            status_code=303,
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7200,
        )

        return response

    # -------------------------
    # API request
    # -------------------------

    response = JSONResponse(
        content={
            "message": "Login successful.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7200,
    )

    return response


# =========================================================
# TOKEN LOGIN
# =========================================================

@router.post("/token")
def token(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    API endpoint for obtaining a JWT access token.
    """

    email = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not verify_password(
        password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# =========================================================
# SESSION
# =========================================================

@router.get("/session")
def session(
    user=Depends(optional_user),
):
    """
    Return the currently authenticated user.

    If the user is not logged in, logged_in is false.
    """

    if not user:

        return {
            "logged_in": False,
            "user": None,
        }

    return {
        "logged_in": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }


# =========================================================
# LOGOUT
# =========================================================

@router.get("/logout")
@router.post("/logout")
def logout():
    """
    Clear the authentication cookie.
    """

    response = RedirectResponse(
        url="/",
        status_code=303,
    )

    response.delete_cookie(
        key="access_token",
    )

    return response