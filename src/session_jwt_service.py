import json
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import HTTPException
from starlette import status

from src.config import settings
from src.session_storage import SessionStorage


class JWTService:
    def __init__(self, storage: SessionStorage | None = None):
        self.__session_storage = storage or SessionStorage()

    async def create_session_token(
        self, *, subject: str, data: dict, token_type: str
    ) -> str:
        await self.__session_storage.insert_token(subject, json.dumps(data))
        return self._create_jw_token({"sub": subject, "typ": token_type})

    async def get_session_data(
        self, jw_token: str, expected_type: str | None = None
    ) -> dict:
        payload = self._decode(jw_token)

        if expected_type and payload.get("typ") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        subject = payload.get("sub")
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        raw = await self.__session_storage.get_user_by_token(subject)
        if not raw:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
            )

        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")

        return json.loads(raw)

    @staticmethod
    def _create_jw_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def _decode(jw_token: str) -> dict:
        try:
            return jwt.decode(
                jw_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
