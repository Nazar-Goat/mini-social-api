from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from src.likes.models import Like
from src.repositories import SQLRepository


class LikeRepository(SQLRepository):
    model = Like

    async def get_like(self, post_id: int, user_id: int) -> Like | None:
        stmt = select(self.model).where(
            self.model.post_id == post_id,
            self.model.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_like(self, post_id: int, user_id: int) -> Like | None:
        like = Like(post_id=post_id, user_id=user_id)
        try:
            self.session.add(like)
            await self.session.flush()
            await self.session.refresh(like)
            return like
        except IntegrityError:
            await self.session.rollback()
            return None

    async def remove_like(self, post_id: int, user_id: int) -> None:
        stmt = delete(self.model).where(
            self.model.post_id == post_id,
            self.model.user_id == user_id,
        )
        await self.session.execute(stmt)