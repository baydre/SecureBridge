from fastapi import APIRouter
from app.api.routes import auth, keys

api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router)
api_router.include_router(keys.router)

__all__ = ["api_router"]