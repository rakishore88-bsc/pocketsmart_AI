from fastapi import APIRouter
from app.auth import CurrentUser
from app.database import get_history

router = APIRouter()

@router.get("/history")
async def api_history(user: CurrentUser):
    return {"history": get_history(user["id"], 50)}

@router.get("/session-info")
async def session_info(user: CurrentUser):
    return {"logged_in": True, "user_id": user["id"], "name": user["name"], "email": user["email"]}

@router.get("/session-data")
async def session_data(user: CurrentUser):
    history = get_history(user["id"], 10)
    return {"user": user, "recent_recommendations": history}
