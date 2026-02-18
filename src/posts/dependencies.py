from fastapi.params import Depends
from src.dependencies import get_session
from src.posts.repositories import PostRepository
from src.posts.services import PostService
from sqlalchemy.ext.asyncio import AsyncSession


async def get_post_repository(session: AsyncSession = Depends(get_session)) -> PostRepository:
    return PostRepository(session)

async def get_post_service(post_repository: PostRepository = Depends(get_post_repository)) -> PostService:
    return PostService(post_repository)