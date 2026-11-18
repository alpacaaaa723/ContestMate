from fastapi import APIRouter
from app.api.v1.endpoints import (
    contests,
    preferences,
    bookmarks,
    calendar,
    notifications,
    admin
)

api_router = APIRouter()

api_router.include_router(contests.router, prefix="/contests", tags=["contests"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
