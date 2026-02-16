from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies import get_session
from src.users.repositories import UserRepository
from src.users.services import UserService

async def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

async def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)
