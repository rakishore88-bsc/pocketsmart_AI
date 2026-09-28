from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.auth import CurrentUser
from app.database import save_history
from app.models.schemas import HomeRequest, JewelryRequest, PartyRequest
from app.services.gemini_service import GeminiService

router = APIRouter()
service = GeminiService()
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/generate-home")
async def generate_home(data: HomeRequest, user: CurrentUser):
    result = service.home(data)
    save_history(user["id"], "home", data.model_dump(), result.model_dump())
    return result


@router.post("/generate-party")
async def generate_party(data: PartyRequest, user: CurrentUser):
    result = service.party(data)
    save_history(user["id"], "party", data.model_dump(), result.model_dump())
    return result


@router.post("/generate-jewelry")
async def generate_jewelry(
    user: CurrentUser,
    budget: float = Form(...),
    currency: str = Form("INR"),
    occasion: str = Form(...),
    style: str = Form("elegant"),
    metal: str = Form("any"),
    outfit_description: str = Form(""),
    notes: str = Form(""),
    outfit_image: UploadFile | None = File(default=None),
):
    data = JewelryRequest(budget=budget, currency=currency, occasion=occasion, style=style, metal=metal, outfit_description=outfit_description, notes=notes)
    image_bytes = None
    mime_type = None
    if outfit_image and outfit_image.filename:
        if outfit_image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(400, "Only JPG, PNG, and WEBP images are supported")
        image_bytes = await outfit_image.read()
        if len(image_bytes) > 5 * 1024 * 1024:
            raise HTTPException(413, "Image must be 5 MB or smaller")
        mime_type = outfit_image.content_type
    result = service.jewelry(data, image_bytes, mime_type)
    save_history(user["id"], "jewelry", data.model_dump(), result.model_dump())
    return result


@router.get("/recommendations-details/{history_id}")
async def recommendation_details(history_id: int, user: CurrentUser):
    from app.database import get_history
    matches = [x for x in get_history(user["id"], 100) if x["id"] == history_id]
    if not matches:
        raise HTTPException(404, "Recommendation not found")
    return matches[0]
