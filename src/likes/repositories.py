from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.likes.models import Like

class LikeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_like_by_id(self, like_id: int) -> Like | None:
        query = (
            select(Like)
            .options(joinedload(Like.post), joinedload(Like.user))
            .where(Like.id == like_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_likes_by_post_id(self, post_id: int) -> list[Like]:
        query = (
            select(Like)
            .options(joinedload(Like.user))
            .where(Like.post_id == post_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_like(self, like: Like) -> Like:
        self.session.add(like)
        await self.session.flush()
        await self.session.refresh(like)
        return like     
    
    async def delete_like(self, like: Like) -> None:
        await self.session.delete(like)
        await self.session.flush()

    