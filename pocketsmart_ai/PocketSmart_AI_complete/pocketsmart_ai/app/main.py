from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.routes import auth, history, pages, planners


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("instance").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    init_db()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, description="Budget-aware AI recommendation assistant", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(planners.router, prefix="/api")
app.include_router(history.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name, "gemini_configured": bool(settings.gemini_api_key), "model": settings.gemini_model}


@app.get("/startup")
async def startup_status():
    return await health()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
