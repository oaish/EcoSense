import sys
from pathlib import Path
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure EcoSense repository root is in sys.path so the 'ai' package can be imported directly
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "EcoSense API"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ecosense"

    JWT_SECRET_KEY: str = "ecosense_dev_jwt_secret_key_dbit_mumbai_2026_super_secure_entropy"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://ecosenseapp.site",
        "https://www.ecosenseapp.site",
    ]

    # AI Classification Settings
    CLASSIFICATION_MODEL_PATH: str = "ai/models/waste_classifier_v2.pkl"
    CLASSIFICATION_MODEL_VERSION: str = "v2.0-fastai"
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.70

    # AI Prediction Settings
    PREDICTION_HORIZON_MINUTES: int = 120
    MIN_PREDICTION_READINGS: int = 3
    PREDICTION_MODEL_VERSION: str = "baseline-v1"

    # Analytics Settings
    DEFAULT_ANALYTICS_DAYS: int = 30
    HIGH_FILL_THRESHOLD: float = 80.0

    # Campus Configuration
    CAMPUS_TIMEZONE: str = "Asia/Kolkata"

    # Firebase Cloud Messaging Web Push Settings
    FIREBASE_PUSH_ENABLED: bool = False
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = None
    PUBLIC_FRONTEND_URL: str = "https://ecosenseapp.site"
    PUBLIC_BACKEND_URL: str = "https://api.ecosenseapp.site"

    # Development seed user credentials (for local dev and testing only)
    DEV_ADMIN_EMAIL: str = "admin@dbit.in"
    DEV_ADMIN_PASSWORD: str = "adminpassword"
    DEV_STUDENT_EMAIL: str = "student@dbit.in"
    DEV_STUDENT_PASSWORD: str = "studentpassword"
    DEV_COLLECTOR_EMAIL: str = "collector@dbit.in"
    DEV_COLLECTOR_PASSWORD: str = "collectorpassword"
    DEV_STAFF_EMAIL: str = "staff@dbit.in"
    DEV_STAFF_PASSWORD: str = "staffpassword"


settings = Settings()

