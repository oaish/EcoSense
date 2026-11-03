from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    attendance,
    auth,
    bins,
    classification,
    collections,
    disposals,
    fill_readings,
    gamification,
    locations,
    notifications,
    predictions,
    processing,
    reports,
    rewards,
    tasks,
    users,
    waste_types,
)

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    locations.router,
    prefix="/locations",
    tags=["Locations"],
)

api_router.include_router(
    waste_types.router,
    prefix="/waste-types",
    tags=["Waste Types"],
)

api_router.include_router(
    bins.router,
    prefix="/bins",
    tags=["Bins"],
)

api_router.include_router(
    fill_readings.router,
    tags=["Fill Readings"],
)

api_router.include_router(
    collections.router,
    prefix="/collections",
    tags=["Collections"],
)

api_router.include_router(
    disposals.router,
    prefix="/disposals",
    tags=["Disposals"],
)

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"],
)

api_router.include_router(
    classification.router,
    prefix="/classification",
    tags=["Classification"],
)

api_router.include_router(
    predictions.router,
    tags=["Predictions"],
)

api_router.include_router(
    processing.router,
    tags=["Recycling & Composting"],
)

api_router.include_router(
    gamification.router,
    prefix="/gamification",
    tags=["Gamification & Rewards"],
)

api_router.include_router(
    rewards.router,
    prefix="/rewards",
    tags=["Rewards"],
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
)

api_router.include_router(
    attendance.router,
    prefix="/attendance",
    tags=["Collector Attendance"],
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Collection Tasks"],
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Push Notifications"],
)





