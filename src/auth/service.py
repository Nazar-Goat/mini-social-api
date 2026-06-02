from fastapi import HTTPException, Request
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse

from src.config import settings
from src.cookies_service import AuthCookieService
from src.modules.auth.schemas import LoginShema
from src.modules.users.schemas import UserSchema
from src.modules.users.utils import verify_password
from src.session_jwt_service import JWTService
from src.session_storage import SessionStorage
from src.unitofwork import IUnitOfWork

ACCESS_COOKIE_NAME = settings.ACCESS_COOKIE_NAME
REFRESH_COOKIE_NAME = settings.REFRESH_COOKIE_NAME


class AuthService:
    def __init__(self):
        self.__unauthorized_user_attempts = {}
        self.__session_storage = SessionStorage()
        self.jwt_service = JWTService(self.__session_storage)
        self.cookies_services = AuthCookieService(self.jwt_service)

    async def login(self, uow: IUnitOfWork, auth_data: LoginShema):
        auth_data.username = auth_data.username.lower()
        async with uow:
            user = await self.__authenticate_user(
                uow, auth_data.username, auth_data.password
            )

            session_data = {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": user.middle_name,
                "role": user.roles[0].code,
                "permissions": [permission.name for permission in user.roles[0].permissions],
            }

            return await self.cookies_services.response_with_auth_cookies(
                content="OK",
                status_code=status.HTTP_200_OK,
                subject=f"crm:{user.id}",
                data=session_data,
                token_type="crm",
                key_access_cookies=settings.ACCESS_COOKIE_NAME,
                key_refresh_cookies=settings.REFRESH_COOKIE_NAME,
            )

    @staticmethod
    async def log_out() -> JSONResponse:
        response = JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True})
        for domain in settings.COOKIE_DOMAINS:
            response.delete_cookie(key=settings.ACCESS_COOKIE_NAME, httponly=True,
                secure=settings.IS_SECURE_COOKIE, path="/", domain=domain)
            response.delete_cookie(key=settings.REFRESH_COOKIE_NAME, httponly=True,
                secure=settings.IS_SECURE_COOKIE, path="/", domain=domain)

        return response

    async def __authenticate_user(
        self, uow: IUnitOfWork, username: str, password: str
    ) -> UserSchema | None:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

        is_user_allow_access = await self.__check_allow_access(username)
        logger.info(f"User allow access: {is_user_allow_access}")
        if not is_user_allow_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have been blocked. Try again later",
            )

        user_model: Users | None = await uow.users.get(email=username)  # noqa

        if not user_model:
            logger.warning("User does not exist")
            await self.__register_failed_attempt(username)
            raise credentials_exception

        if not verify_password(password, user_model.hashed_password):
            logger.warning("Password is not valid")
            await self.__register_failed_attempt(username)
            raise credentials_exception

        self.__unauthorized_user_attempts.pop(username, None)
        return user_model

    async def __register_failed_attempt(self, username: str):
        existed_attempts = self.__unauthorized_user_attempts.get(username, 0)
        existed_attempts += 1
        if existed_attempts >= settings.FAILED_LOGIN_ATTEMPTS:
            await self.__session_storage.insert_unauthorized_user(username)
            self.__unauthorized_user_attempts.pop(username, None)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="There have been too many failed login attempts",
            )
        self.__unauthorized_user_attempts[username] = existed_attempts

    async def __check_allow_access(self, username: str) -> bool:
        user = await self.__session_storage.get_banned_user_by_username(username)
        if user:
            return False
        return True

    async def get_me(self, request: Request) -> UserSchema:
        jw_token = request.cookies.get(ACCESS_COOKIE_NAME)
        if not jw_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        user_data = await self.jwt_service.get_session_data(
            jw_token, expected_type="crm"
        )
        return UserSchema(**user_data)
