from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from src.config import settings


class SessionStorage:
    __KEY_TTL = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    __FAILED_LOGIN_ATTEMPTS_TIMEOUT = int(settings.FAILED_LOGIN_ATTEMPTS_TIMEOUT * 60)
    __WSS_KEY_TTL = settings.WSS_TOKEN_TTL

    def __init__(self):
        self.__redis_auth_db = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASS,
            db=settings.REDIS_AUTH_DB,
        )
        self.__redis_throttling_db = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASS,
            db=settings.REDIS_THROTTLING_DB,
        )

    async def ping(self) -> bool:
        try:
            auth_db_ping = await self.__redis_auth_db.ping()
            throttling_db_ping = await self.__redis_throttling_db.ping()
            return auth_db_ping and throttling_db_ping
        except ConnectionError:
            return False

    async def insert_token(self, user_token: str, user_info: str) -> None:
        await self.__redis_auth_db.setex(
            f"user:{user_token}", self.__KEY_TTL, user_info
        )

    async def get_user_by_token(self, user_token: str) -> str:
        result = await self.__redis_auth_db.get(f"user:{user_token}")
        return result

    async def insert_unauthorized_user(self, username: str):
        await self.__redis_throttling_db.setex(
            username, self.__FAILED_LOGIN_ATTEMPTS_TIMEOUT, username
        )

    async def get_banned_user_by_username(self, username: str):
        result = await self.__redis_throttling_db.get(username)
        return result

    async def create_ws_token(self, token: str, user_id: str):
        await self.__redis_auth_db.setex(f"wss:{token}", self.__WSS_KEY_TTL, user_id)

    async def lookup_ws_token(self, token: str) -> str | None:
        user_id = await self.__redis_auth_db.get(f"wss:{token}")
        if user_id is not None:
            await self.__redis_auth_db.delete(f"wss:{token}")
            return user_id.decode()
        return None
