from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from src.dependencies import CurrentUser, UOW
from src.posts.schemas import PostCreate, PostOut, PostUpdate
from src.posts.services import PostService
from src.users.models import User


posts_router = APIRouter(prefix="/posts", tags=["Posts"])

post_service = PostService()


@posts_router.post(
    "",
    response_model=PostOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post_data: PostCreate,
    uow: UOW,
    current_user: CurrentUser,
) -> PostOut:
    return await post_service.create_post(uow, post_data, current_user.id)


@posts_router.get(
    "",
    response_model=list[PostOut],
    status_code=status.HTTP_200_OK,
)
async def get_posts(
    uow: UOW,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    author_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    sort: Literal["created_at", "likes"] = Query(default="created_at"),
    order: Literal["asc", "desc"] = Query(default="desc"),
) -> list[PostOut]:
    return await post_service.get_posts(
        uow=uow,
        limit=limit,
        offset=offset,
        author_id=author_id,
        search=search,
        sort=sort,
        order=order,
    )


@posts_router.get(
    "/{post_id}",
    response_model=PostOut,
    status_code=status.HTTP_200_OK,
)
async def get_post(post_id: int, uow: UOW) -> PostOut:
    return await post_service.get_post(uow, post_id)


@posts_router.put(
    "/{post_id}",
    response_model=PostOut,
    status_code=status.HTTP_200_OK,
)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    uow: UOW,
    current_user: CurrentUser,
) -> PostOut:
    return await post_service.update_post(uow, post_id, post_data, current_user.id)


@posts_router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: int,
    uow: UOW,
    current_user: CurrentUser,
) -> None:
    await post_service.delete_post(uow, post_id, current_user.id)