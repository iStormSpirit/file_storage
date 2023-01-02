from fastapi import APIRouter

from .file import router as router_file
from .user import router as router_user

api_router = APIRouter()
api_router.include_router(router_user)
api_router.include_router(router_file)
