from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.unitofwork import IUnitOfWork, UnitOfWork
from src.users.auth import decode_token
from src.users.models import User
from src.users.repositories import UserRepository
from src.database.core import async_session_maker


bearer_scheme = HTTPBearer()


async def get_uow() -> IUnitOfWork:
    return UnitOfWork()


UOW = Annotated[IUnitOfWork, Depends(get_uow)]


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    payload = decode_token(token.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    raw_user_id: str = payload.get("sub")

    if raw_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    try:
        user_id = int(raw_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    async with async_session_maker() as session:
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]