from fastapi import HTTPException, status

from src.posts.schemas import PostCreate, PostOut, PostUpdate
from src.redis.service import redis_service
from src.unitofwork import IUnitOfWork


class PostService:

    @staticmethod
    async def create_post(uow: IUnitOfWork, post_data: PostCreate, user_id: int) -> PostOut:
        async with uow:
            post = await uow.posts.create(
                {
                    "title": post_data.title,
                    "content": post_data.content,
                    "author_id": user_id,
                }
            )
            await uow.commit()

        await redis_service.invalidate_posts_cache()

        return PostOut.model_validate(post)

    @staticmethod
    async def get_post(uow: IUnitOfWork, post_id: int) -> PostOut:
        async with uow:
            post = await uow.posts.get_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )

        return PostOut.model_validate(post)

    @staticmethod
    async def get_posts(
        uow: IUnitOfWork,
        limit: int,
        offset: int,
        author_id: int | None,
        search: str | None,
        sort: str,
        order: str,
    ) -> list[PostOut]:
        # Спочатку пробуємо кеш — тільки для дефолтних параметрів (без фільтрів)
        cached = await redis_service.get_cached_posts(limit, offset, sort, order, search, author_id)
        if cached is not None:
            return [PostOut(**post) for post in cached]

        async with uow:
            posts = await uow.posts.get_list(
                limit=limit,
                offset=offset,
                author_id=author_id,
                search=search,
                sort=sort,
                order=order,
            )

        result = [PostOut.model_validate(post) for post in posts]

        await redis_service.set_cached_posts(
            limit, offset, sort, order, search, author_id,
            [post.model_dump(mode="json") for post in result],
        )

        return result

    @staticmethod
    async def update_post(
        uow: IUnitOfWork,
        post_id: int,
        post_data: PostUpdate,
        user_id: int,
    ) -> PostOut:
        async with uow:
            post = await uow.posts.get_by_id(post_id)

            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found",
                )

            if post.author_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update this post",
                )

            update_data = post_data.model_dump(exclude_unset=True)
            updated_post = await uow.posts.update(post_id, update_data)

            await uow.commit()

        await redis_service.invalidate_posts_cache()

        return PostOut.model_validate(updated_post)

    @staticmethod
    async def delete_post(uow: IUnitOfWork, post_id: int, user_id: int) -> None:
        async with uow:
            post = await uow.posts.get_by_id(post_id)

            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found",
                )

            if post.author_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this post",
                )

            await uow.posts.remove(post_id)
            await uow.commit()

        await redis_service.invalidate_posts_cache()