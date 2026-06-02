import secrets

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from src.config import settings
from src.session_jwt_service import JWTService


class AuthCookieService:

    def __init__(self, jwt_service: JWTService | None = None):
        self.__jwt_service = jwt_service or JWTService()

    async def response_with_auth_cookies(
        self,
        *,
        content: dict | str,
        status_code: int,
        subject: str,
        data: dict,
        token_type: str,
        key_access_cookies: str,
        key_refresh_cookies: str
    ) -> JSONResponse:
        is_dev = settings.ENVIRONMENT == "DEV"

        access_jwt = await self.__jwt_service.create_session_token(
            subject=subject,
            data=data,
            token_type=token_type,
        )
        refresh_token = secrets.token_urlsafe(64)

        if isinstance(content, dict):
            response_content = dict(content)
        else:
            response_content = {"detail": content}

        if is_dev:
            response_content["token"] = access_jwt

        response = JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(response_content),
        )

        for domain in settings.COOKIE_DOMAINS:
            response.set_cookie(
                key=key_access_cookies,
                value=access_jwt,
                httponly=True,
                secure=settings.IS_SECURE_COOKIE,
                samesite="lax" if settings.IS_LAX_COOKIE else "none",
                path="/",
                max_age=settings.ACCESS_TTL_MINUTES * 60,
                domain=domain
            )

        for domain in settings.COOKIE_DOMAINS:
            response.set_cookie(
                key=key_refresh_cookies,
                value=refresh_token,
                httponly=True,
                secure=settings.IS_SECURE_COOKIE,
                samesite="lax" if settings.IS_LAX_COOKIE else "none",
                path="/",
                max_age=settings.REFRESH_TTL_DAYS * 24 * 60 * 60,
                domain=domain
            )

        return response
