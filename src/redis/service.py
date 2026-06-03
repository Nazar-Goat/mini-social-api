import json

from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from src.config import settings


POSTS_CACHE_TTL = 30          # seconds
LIKE_RATE_LIMIT = 30          # max likes per window
LIKE_RATE_WINDOW = 60         # seconds


class RedisService:
    def __init__(self) -> None:
        self._cache = Redis(
            host=settings.REDIS_HOST,
            port=int(settings.REDIS_PORT),
            password=settings.REDIS_PASS,
            db=int(settings.REDIS_QUEUE_DB),
            decode_responses=True,
        )
        self._throttle = Redis(
            host=settings.REDIS_HOST,
            port=int(settings.REDIS_PORT),
            password=settings.REDIS_PASS,
            db=int(settings.REDIS_THROTTLING_DB),
            decode_responses=True,
        )

    # --- Posts cache ---

    @staticmethod
    def _posts_cache_key(limit: int, offset: int, sort: str, order: str, search: str | None, author_id: int | None) -> str:
        return f"posts:limit={limit}:offset={offset}:sort={sort}:order={order}:search={search}:author={author_id}"

    async def get_cached_posts(
        self,
        limit: int,
        offset: int,
        sort: str,
        order: str,
        search: str | None,
        author_id: int | None,
    ) -> list | None:
        key = self._posts_cache_key(limit, offset, sort, order, search, author_id)
        try:
            raw = await self._cache.get(key)
            if raw:
                return json.loads(raw)
        except ConnectionError:
            logger.warning("Redis unavailable, skipping cache read")
        return None

    async def set_cached_posts(
        self,
        limit: int,
        offset: int,
        sort: str,
        order: str,
        search: str | None,
        author_id: int | None,
        data: list,
    ) -> None:
        key = self._posts_cache_key(limit, offset, sort, order, search, author_id)
        try:
            await self._cache.setex(key, POSTS_CACHE_TTL, json.dumps(data))
        except ConnectionError:
            logger.warning("Redis unavailable, skipping cache write")

    async def invalidate_posts_cache(self) -> None:
        try:
            keys = await self._cache.keys("posts:*")
            if keys:
                await self._cache.delete(*keys)
        except ConnectionError:
            logger.warning("Redis unavailable, skipping cache invalidation")

    # --- Like rate limiting ---

    async def check_like_rate_limit(self, user_id: int) -> bool:
        key = f"like_rate:{user_id}"
        try:
            count = await self._throttle.incr(key)
            if count == 1:
                await self._throttle.expire(key, LIKE_RATE_WINDOW)
            return count <= LIKE_RATE_LIMIT
        except ConnectionError:
            logger.warning("Redis unavailable, skipping rate limit check")
            return True


redis_service = RedisService()  # noqa