import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "AI-Enhanced Sophisticated Phishing Detection System"
    
    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "phishing_detection"
    
    # Auth
    JWT_SECRET: str = "super_secret_phishing_detection_jwt_key_2026_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Privacy
    STORE_RAW_INPUT: bool = False
    
    # ML
    MODEL_PATH: str = "./ml/saved_models"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
