from fastapi import APIRouter, status

from src.dependencies import CurrentUser, UOW
from src.likes.schemas import LikeResponse
from src.likes.services import LikeService


likes_router = APIRouter(prefix="/posts", tags=["Likes"])

like_service = LikeService()


@likes_router.post(
    "/{post_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_200_OK,
)
async def like_post(
    post_id: int,
    uow: UOW,
    current_user: CurrentUser,
) -> LikeResponse:
    return await like_service.like_post(uow, post_id, current_user.id)


@likes_router.delete(
    "/{post_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_200_OK,
)
async def unlike_post(
    post_id: int,
    uow: UOW,
    current_user: CurrentUser,
) -> LikeResponse:
    return await like_service.unlike_post(uow, post_id, current_user.id)