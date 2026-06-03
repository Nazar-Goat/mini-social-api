from fastapi import HTTPException, status

from src.likes.schemas import LikeResponse
from src.redis.service import redis_service
from src.unitofwork import IUnitOfWork


class LikeService:

    @staticmethod
    async def like_post(uow: IUnitOfWork, post_id: int, user_id: int) -> LikeResponse:
        # Rate limit: 30 лайків / 60 секунд на користувача
        allowed = await redis_service.check_like_rate_limit(user_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Like rate limit exceeded. Try again later.",
            )

        async with uow:
            post = await uow.posts.get_by_id(post_id)

            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found",
                )

            existing = await uow.likes.get_like(post_id=post_id, user_id=user_id)

            if existing:
                return LikeResponse(message="Post already liked", action="none")

            created = await uow.likes.create_like(post_id=post_id, user_id=user_id)

            if not created:
                # IntegrityError — race condition, лайк вже є
                return LikeResponse(message="Post already liked", action="none")

            await uow.commit()

        await redis_service.invalidate_posts_cache()

        return LikeResponse(message="Post liked", action="liked")

    @staticmethod
    async def unlike_post(uow: IUnitOfWork, post_id: int, user_id: int) -> LikeResponse:
        async with uow:
            existing = await uow.likes.get_like(post_id=post_id, user_id=user_id)

            if not existing:
                return LikeResponse(message="Post not liked yet", action="none")

            await uow.likes.remove_like(post_id=post_id, user_id=user_id)
            await uow.commit()

        await redis_service.invalidate_posts_cache()

        return LikeResponse(message="Post unliked", action="unliked")