from fastapi import APIRouter, Depends, status

from src.dependencies import CurrentUser, UOW
from src.users.schemas import TokenOut, UserLogin, UserOut, UserRegister
from src.users.services import UserService


users_router = APIRouter(prefix="/users", tags=["Users"])

user_service = UserService()


@users_router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserRegister, uow: UOW) -> UserOut:
    return await user_service.register(uow, user_data)


@users_router.post(
    "/login",
    response_model=TokenOut,
    status_code=status.HTTP_200_OK,
)
async def login(user_data: UserLogin, uow: UOW) -> TokenOut:
    return await user_service.login(uow, user_data)


@users_router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
)
async def get_me(current_user: CurrentUser) -> UserOut:
    return UserOut.model_validate(current_user)