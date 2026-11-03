from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup actions: safely initialize push service if enabled
    if settings.FIREBASE_PUSH_ENABLED:
        from app.services.push_notification_service import push_notification_service
        push_notification_service._ensure_firebase_initialized()
    yield
    # Shutdown actions


app = FastAPI(
    title=settings.APP_NAME,
    description="EcoSense Backend API - AI-Based Zero Waste Campus Management Platform for Don Bosco Institute of Technology (DBIT), Mumbai",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

cors_origins = list(settings.CORS_ORIGINS)
if settings.PUBLIC_FRONTEND_URL and settings.PUBLIC_FRONTEND_URL not in cors_origins:
    cors_origins.append(settings.PUBLIC_FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="Endpoint for liveness and uptime checks.",
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}
