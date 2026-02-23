from fastapi import APIRouter, Depends, status

from src.likes.dependencies import get_like_service
from src.likes.schemas import LikeResponse
from src.likes.services import LikeService
from src.users.dependencies import get_current_user
from src.users.models import User

router = APIRouter(prefix="/posts", tags=["likes"])

@router.post("/{post_id}/like", response_model=LikeResponse, status_code=status.HTTP_200_OK)
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends(get_like_service)
):
    result = await like_service.like_post(post_id, current_user.id)
    return LikeResponse(**result)

@router.delete("/{post_id}/like", response_model=LikeResponse, status_code=status.HTTP_200_OK)
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends(get_like_service)
):
    result = await like_service.unlike_post(post_id, current_user.id)
    return LikeResponse(**result)
