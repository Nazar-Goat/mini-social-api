from sqlalchemy import select

from src.repositories import SQLRepository
from src.users.models import User


class UserRepository(SQLRepository):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(self.model).where(self.model.email == email)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(self.model).where(self.model.id == user_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()