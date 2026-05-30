from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_session
from src.likes.repositories import LikeRepository
from src.likes.services import LikeService
from src.posts.repositories import PostRepository

async def get_like_repository(session: AsyncSession = Depends(get_session)) -> LikeRepository:
    return LikeRepository(session)

async def get_like_service(session: AsyncSession = Depends(get_session)) -> LikeService:
    like_repository = LikeRepository(session)
    post_repository = PostRepository(session)
    return LikeService(like_repository, post_repository)

