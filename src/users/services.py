from users.repositories import UserRepository
from users.auth import  get_password_hash, create_access_token, create_refresh_token
from users.schemas import UserRegister, UserLogin, UserOut, TokenOut

from users.models import User

from fastapi import HTTPException, status

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, user_data: UserRegister) -> UserOut:
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        password_hash = get_password_hash(user_data.password)

        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            email=user_data.email,
            password=password_hash
        )

        created_user = await self.user_repository.create_user(new_user)
        return UserOut.model_validate(created_user)
