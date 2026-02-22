from src.likes.repositories import LikeRepository
from src.likes.models import Like

from src.posts.repositories import PostRepository

from fastapi import HTTPException, status

class LikeService:
    def __init__(self, like_repository: LikeRepository, post_repository: PostRepository):
        self.like_repository = like_repository
        self.post_repository = post_repository

    async def like_post(self, post_id: int, user_id: int) -> dict:
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        existing_like = await self.like_repository.get_like(post_id, user_id)
        if existing_like:
            await self.like_repository.session.commit()
            return {"message": "Post already liked", "action": "none"}
        
        like = Like(post_id=post_id, user_id=user_id)
        created_like = await self.like_repository.create_like(like)

        if not created_like:
            self.like_repository.session.commit()
            return {"message": "Post already liked", "action": "none"}
        
        await self.like_repository.session.commit()
        return {"message": "Post liked", "action": "liked"}
    
    async def unlike_post(self, post_id: int, user_id: int) -> dict:
        like = await self.like_repository.get_like(post_id, user_id)
        if not like:
            await self.like_repository.session.commit()
            return {"message": "Post not liked yet", "action": "none"}
        
        await self.like_repository.delete_like(like)
        await self.like_repository.session.commit()
        return {"message": "Post unliked", "action": "unliked"}
    


