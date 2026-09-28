import io
import json

from contextlib import asynccontextmanager

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from fastapi.templating import Jinja2Templates

from PIL import (
    Image,
    UnidentifiedImageError,
)

from sqlalchemy.orm import Session

from .auth import (
    create_access_token,
    current_user,
    hash_password,
    optional_user,
    verify_password,
)

from .config import (
    APP_NAME,
    CORS_ORIGINS,
    MAX_IMAGE_MB,
)

from .database import (
    Base,
    engine,
    get_db,
)

from .gemini_utils import (
    generate_home,
    generate_party,
    generate_jewelry,
)

from .models import (
    RecommendationHistory,
    User,
)


templates = Jinja2Templates(
    directory="templates"
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(
        bind=engine
    )

    yield


app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_history(
    db: Session,
    user: User,
    category: str,
    budget: float,
    request_data: dict,
    response_data: dict,
):

    record = RecommendationHistory(
        user_id=user.id,
        category=category,
        budget=budget,
        request_json=json.dumps(
            request_data
        ),
        response_json=json.dumps(
            response_data
        ),
    )

    db.add(record)
    db.commit()


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get(
    "/",
    response_class=HTMLResponse
)
def home(
    request: Request,
    user=Depends(optional_user),
):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "app_name": APP_NAME,
        },
    )


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

@app.get(
    "/login",
    response_class=HTMLResponse
)
def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "app_name": APP_NAME,
        },
    )


@app.get(
    "/register",
    response_class=HTMLResponse
)
def register_page(request: Request):

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "app_name": APP_NAME,
        },
    )


@app.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    username = username.strip()
    email = email.strip().lower()

    if len(password) < 8:

        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": (
                    "Password must be at least "
                    "8 characters."
                ),
                "app_name": APP_NAME,
            },
            status_code=400,
        )

    existing = db.query(User).filter(
        (User.username == username)
        | (User.email == email)
    ).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail=(
                "Username or email already exists."
            ),
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )

    db.add(user)
    db.commit()

    return RedirectResponse(
        "/login?registered=1",
        status_code=303,
    )


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    email = email.strip().lower()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user or not verify_password(
        password,
        user.password_hash
    ):

        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password.",
                "app_name": APP_NAME,
            },
            status_code=401,
        )

    response = RedirectResponse(
        "/dashboard",
        status_code=303,
    )

    response.set_cookie(
        "access_token",
        create_access_token(user.id),
        httponly=True,
        samesite="lax",
        max_age=7200,
    )

    return response


@app.post("/token")
def token(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    email = email.strip().lower()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user or not verify_password(
        password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": create_access_token(
            user.id
        ),
        "token_type": "bearer",
    }


@app.get("/logout")
def logout():

    response = RedirectResponse(
        "/",
        status_code=303
    )

    response.delete_cookie(
        "access_token"
    )

    return response


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard(
    request: Request,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):

    history = (
        db.query(RecommendationHistory)
        .filter_by(user_id=user.id)
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .limit(10)
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "history": history,
            "app_name": APP_NAME,
        },
    )


@app.get(
    "/history",
    response_class=HTMLResponse
)
def history(
    request: Request,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):

    records = (
        db.query(RecommendationHistory)
        .filter_by(user_id=user.id)
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .all()
    )

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "user": user,
            "history": records,
            "app_name": APP_NAME,
        },
    )


# ---------------------------------------------------------
# PLANNER PAGES
# ---------------------------------------------------------

@app.get(
    "/planner/{category}",
    response_class=HTMLResponse,
)
def planner(
    request: Request,
    category: str,
    user=Depends(current_user),
):

    allowed = {
        "home",
        "party",
        "jewelry",
    }

    if category not in allowed:

        raise HTTPException(
            status_code=404,
            detail="Planner not found",
        )

    return templates.TemplateResponse(
        f"{category}_planner.html",
        {
            "request": request,
            "user": user,
            "app_name": APP_NAME,
        },
    )


# ---------------------------------------------------------
# HOME RECOMMENDATIONS
# ---------------------------------------------------------

@app.post("/generate-home")
def generate_home_endpoint(
    payload: dict,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):

    try:
        budget = float(
            payload.get("budget", 0)
        )
    except (ValueError, TypeError):
        budget = 0

    if budget <= 0:

        raise HTTPException(
            status_code=422,
            detail="Budget must be greater than zero.",
        )

    result = generate_home(
        payload
    )

    save_history(
        db,
        user,
        "home",
        budget,
        payload,
        result,
    )

    return result


# ---------------------------------------------------------
# PARTY RECOMMENDATIONS
# ---------------------------------------------------------

@app.post("/generate-party")
def generate_party_endpoint(
    payload: dict,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):

    try:
        budget = float(
            payload.get("budget", 0)
        )

        guests = int(
            payload.get("guests", 0)
        )

    except (ValueError, TypeError):

        raise HTTPException(
            status_code=422,
            detail="Invalid budget or guest count.",
        )

    if budget <= 0 or guests <= 0:

        raise HTTPException(
            status_code=422,
            detail=(
                "Budget and guests must "
                "be positive."
            ),
        )

    result = generate_party(
        payload
    )

    save_history(
        db,
        user,
        "party",
        budget,
        payload,
        result,
    )

    return result


# ---------------------------------------------------------
# JEWELRY RECOMMENDATIONS
# ---------------------------------------------------------

@app.post("/generate-jewelry")
async def generate_jewelry_endpoint(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form(""),
    outfit_description: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    user=Depends(current_user),
    db: Session = Depends(get_db),
):

    if budget <= 0:

        raise HTTPException(
            status_code=422,
            detail="Budget must be greater than zero.",
        )

    image = None

    if outfit_image and outfit_image.filename:

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if outfit_image.content_type not in allowed_types:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Use JPG, PNG, or WEBP."
                ),
            )

        data = await outfit_image.read()

        if len(data) > (
            MAX_IMAGE_MB * 1024 * 1024
        ):

            raise HTTPException(
                status_code=413,
                detail=(
                    f"Image must be <= "
                    f"{MAX_IMAGE_MB} MB."
                ),
            )

        try:

            image = Image.open(
                io.BytesIO(data)
            ).convert("RGB")

        except UnidentifiedImageError:

            raise HTTPException(
                status_code=400,
                detail="Invalid image file.",
            )

    request_data = {
        "budget": budget,
        "occasion": occasion,
        "style": style,
        "outfit_description": outfit_description,
    }

    result = generate_jewelry(
        request_data,
        image,
    )

    save_history(
        db,
        user,
        "jewelry",
        budget,
        request_data,
        result,
    )

    return result


# ---------------------------------------------------------
# RECOMMENDATION DETAILS
# ---------------------------------------------------------

@app.get(
    "/recommendations-details/{recommendation_id}"
)
def recommendation_details(
    recommendation_id: int,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):

    record = (
        db.query(RecommendationHistory)
        .filter_by(
            id=recommendation_id,
            user_id=user.id,
        )
        .first()
    )

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Recommendation not found.",
        )

    return {
        "id": record.id,
        "category": record.category,
        "budget": record.budget,
        "request": json.loads(
            record.request_json
        ),
        "response": json.loads(
            record.response_json
        ),
        "created_at": (
            record.created_at.isoformat()
        ),
    }


# ---------------------------------------------------------
# SESSION
# ---------------------------------------------------------

@app.get("/session-info")
def session_info(
    user=Depends(current_user)
):

    return {
        "logged_in": True,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }


@app.get("/session-data")
def session_data(
    user=Depends(current_user),
    db: Session = Depends(get_db),
):

    count = (
        db.query(RecommendationHistory)
        .filter_by(user_id=user.id)
        .count()
    )

    return {
        "user_id": user.id,
        "recommendation_count": count,
    }


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": APP_NAME,
    }


# ---------------------------------------------------------
# DIRECT EXECUTION
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )