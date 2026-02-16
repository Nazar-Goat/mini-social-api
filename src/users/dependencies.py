from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies import get_session

from src.users.models import User
from src.users.repositories import UserRepository
from src.users.services import UserService

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.users.auth import  to_decode

bearer_scheme = HTTPBearer()

async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session : AsyncSession = Depends(get_session)
) -> User :

    payload = to_decode(token.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user_id: int = int(payload.get("sub"))
    if user_id is None: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    user_repository = UserRepository(session)
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user 

async def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

async def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)

