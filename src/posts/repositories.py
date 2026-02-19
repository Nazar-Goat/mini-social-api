from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.posts.models import Post

class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post_by_id(self, post_id: int) -> Post | None:
        query = select(Post).options(joinedload(Post.author)).where(Post.id == post_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all_posts(self, limit: int=10, offset: int=0) -> list[Post]:
        query = (
            select(Post)
            .options(joinedload(Post.author))
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_post(self, post: Post) -> Post:
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        return post
    
    async def update_post(self, post: Post ) -> Post:
        await self.session.flush()
        await self.session.refresh(post)

    async def delete_post(self, post: Post) -> None:
        await self.session.delete(post)
        await self.session.flush()