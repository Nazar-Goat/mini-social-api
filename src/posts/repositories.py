from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload, selectinload

from src.likes.models import Like
from src.posts.models import Post
from src.repositories import SQLRepository


class PostRepository(SQLRepository):
    model = Post

    async def get_by_id(self, post_id: int) -> Post | None:
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.author),
                selectinload(self.model.likes),
            )
            .where(self.model.id == post_id)
        )
        res = await self.session.execute(stmt)
        post = res.scalar_one_or_none()

        if post is not None:
            post.likes_count = len(post.likes)

        return post

    async def get_list(
        self,
        limit: int,
        offset: int,
        author_id: int | None = None,
        search: str | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> list[Post]:
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.author),
                selectinload(self.model.likes),
            )
        )

        if author_id is not None:
            stmt = stmt.where(self.model.author_id == author_id)

        if search:
            stmt = stmt.where(
                or_(
                    self.model.title.ilike(f"%{search}%"),
                    self.model.content.ilike(f"%{search}%"),
                )
            )

        # Sorting: created_at or likes count
        if sort == "likes":
            likes_count_subq = (
                select(Like.post_id, func.count(Like.id).label("likes_count"))
                .group_by(Like.post_id)
                .subquery()
            )
            stmt = stmt.outerjoin(
                likes_count_subq, self.model.id == likes_count_subq.c.post_id
            )
            order_col = likes_count_subq.c.likes_count
        else:
            order_col = self.model.created_at

        from sqlalchemy import asc, desc
        stmt = stmt.order_by(desc(order_col) if order == "desc" else asc(order_col))
        stmt = stmt.limit(limit).offset(offset)

        res = await self.session.execute(stmt)
        posts = res.unique().scalars().all()

        for post in posts:
            post.likes_count = len(post.likes)

        return posts

    async def create(self, data: dict) -> Post:
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.author),
                selectinload(self.model.likes),
            )
            .where(self.model.id == await self.add(data))
        )
        res = await self.session.execute(stmt)
        post = res.scalar_one()
        post.likes_count = 0
        return post

    async def update(self, post_id: int, data: dict) -> Post:
        await self.edit(element_id=post_id, data=data)
        return await self.get_by_id(post_id)

    async def remove(self, post_id: int) -> None:
        await self.delete(post_id)