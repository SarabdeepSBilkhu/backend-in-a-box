# Auto-generated router imports
from fastapi import APIRouter

from .user import router as user_router

# Combine all routers
api_router = APIRouter()
api_router.include_router(user_router)
