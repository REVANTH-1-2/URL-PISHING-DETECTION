from fastapi import APIRouter, status
from app.database.connection import db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    mongo_status = "connected"
    if db.client is None:
        mongo_status = "disconnected"
    else:
        try:
            await db.client.admin.command('ping')
        except Exception:
            mongo_status = "degraded"
            
    return {
        "status": "healthy",
        "service": "AI-Enhanced Phishing Detection Backend",
        "mongodb": mongo_status,
        "version": "1.0.0"
    }
