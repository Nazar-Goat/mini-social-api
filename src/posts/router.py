from src.posts.dependencies import get_post_service, get_post_repository
from src.users.dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from src.posts.services import PostService
from src.posts.schemas import PostCreate, PostOut, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    post_service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user)
):
    return await post_service.create_post(post_data, current_user.id)

@router.get("/{post_id}", response_model=PostOut, status_code=status.HTTP_200_OK)
async def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service)
):
    return await post_service.get_post(post_id)

@router.get("/", response_model=list[PostOut], status_code=status.HTTP_200_OK)
async def get_posts(
    limit: int = 10,
    offset: int = 0,
    post_service: PostService = Depends(get_post_service)
):
    return await post_service.get_posts(limit, offset)

@router.put("/{post_id}", response_model=PostOut, status_code=status.HTTP_200_OK)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    post_service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user)
):
    return await post_service.update_post(post_id, post_data, current_user.id)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user)
):
    await post_service.delete_post(post_id, current_user.id)

