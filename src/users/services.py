from fastapi import HTTPException, status

from src.unitofwork import IUnitOfWork
from src.users.auth import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from src.users.schemas import TokenOut, UserOut, UserRegister, UserLogin


class UserService:

    @staticmethod
    async def register(uow: IUnitOfWork, user_data: UserRegister) -> UserOut:
        async with uow:
            existing = await uow.users.get_by_email(user_data.email)

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )

            user_id = await uow.users.add(
                {
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "username": user_data.username,
                    "email": user_data.email,
                    "password": get_password_hash(user_data.password),
                }
            )  # noqa

            await uow.commit()

            user = await uow.users.get_by_id(user_id)

        return UserOut.model_validate(user)

    @staticmethod
    async def login(uow: IUnitOfWork, user_data: UserLogin) -> TokenOut:
        async with uow:
            user = await uow.users.get_by_email(user_data.email)

        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return TokenOut(access_token=access_token, refresh_token=refresh_token)