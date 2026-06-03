from fastapi import APIRouter

from src.users.router import users_router
from src.posts.router import posts_router
from src.likes.router import likes_router


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(users_router)
api_router.include_router(posts_router)
api_router.include_router(likes_router)