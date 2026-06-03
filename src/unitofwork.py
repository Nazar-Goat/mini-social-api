from abc import ABC, abstractmethod
from typing import Type

from src.database.core import async_session_maker
from src.likes.repositories import LikeRepository
from src.posts.repositories import PostRepository
from src.users.repositories import UserRepository


class IUnitOfWork(ABC):
    users: UserRepository
    posts: PostRepository
    likes: LikeRepository

    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, *args) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


class UnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self.session_factory = async_session_maker

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.posts = PostRepository(self.session)
        self.likes = LikeRepository(self.session)
        return self

    async def __aexit__(self, *args) -> None:
        await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()