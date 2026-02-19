from src.posts.repositories import PostRepository
from src.posts.schemas import PostCreate, PostUpdate, PostOut
from src.posts.models import Post

from fastapi import HTTPException, status

class PostService:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository

    async def create_post(self, post_data: PostCreate, user_id: int) -> PostOut:
        post = Post(
            title=post_data.title,
            content=post_data.content,
            author_id=user_id
        )
        created_post = await self.post_repository.create_post(post)

        self.post_repository.session.add(created_post)
        await self.post_repository.session.commit()
        await self.post_repository.session.refresh(created_post)

        return PostOut.model_validate(created_post)
    
    async def get_post(self, post_id: int) -> PostOut:
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        return PostOut.model_validate(post)
    
    async def get_posts(self, limit: int=10, offset: int=0) -> list[PostOut]:
        posts = await self.post_repository.get_all_posts(limit, offset)
        return [PostOut.model_validate(post) for post in posts]
    
    async def update_post(self, post_id: int, post_data: PostUpdate, current_user: int) -> PostOut:
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        if post.author_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )
        
        if post_data.title is not None:
            post.title = post_data.title
        if post_data.content is not None:
            post.content = post_data.content
        
        await self.post_repository.update_post(post)
        await self.post_repository.session.commit()
        await self.post_repository.session.refresh(post)

        return PostOut.model_validate(post)
    
    async def delete_post(self, post_id: int, current_user: int) -> None:
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        if post.author_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )
        
        await self.post_repository.delete_post(post)
        await self.post_repository.session.commit()
    

