from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

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
    
    async def get_like(self, post_id: int, user_id: int) -> Like | None:
        query = (
            select(Like)
            .where(Like.post_id == post_id, Like.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def count_post_likes(self, post_id: int) -> int:
        query = select(func.count()).select_from(Like).where(
            Like.post_id == post_id
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def create_like(self, like: Like) -> Like:
        try: 
            self.session.add(like)
            await self.session.flush()
            await self.session.refresh(like)
            return like 
        except IntegrityError:
            await self.session.rollback()
            return None   
    
    async def delete_like(self, like: Like) -> None:
        await self.session.delete(like)
        await self.session.flush()

    