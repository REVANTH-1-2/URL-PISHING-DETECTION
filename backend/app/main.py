import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.scan import router as scan_router
from app.api.analytics import router as analytics_router
from app.api.models_api import router as models_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("phishing_system")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application startup...")
    await connect_to_mongo()
    yield
    logger.info("Shutting down application...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API service for Multi-Modal AI Phishing Detection System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(scan_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(models_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "title": settings.PROJECT_NAME,
        "status": "running",
        "docs": "/docs"
    }
