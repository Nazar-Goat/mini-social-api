from abc import ABC, abstractmethod

from sqlalchemy import UUID, asc, delete, desc, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count, func


class AbstractRepository(ABC):
    @abstractmethod
    async def add(self, data: dict): ...

    @abstractmethod
    async def edit(self, element_id: int | str, data: dict): ...

    @abstractmethod
    async def get(self): ...

    @abstractmethod
    async def get_all(self): ...


class SQLRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, data: dict) -> int | UUID:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit(self, element_id: int | str, data: dict) -> int:
        stmt = (
            update(self.model)
            .values(**data)
            .filter_by(id=element_id)
            .returning(self.model.id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def get(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_elements(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.unique().scalars().all()

    async def get_field(self, field: str, **filter_by):
        stmt = select(getattr(self.model, field)).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_with_limit_offset(
        self,
        limit: int,
        offset: int,
        filter_by: dict,
        order_by: str | None = None,
        order_desc: bool = False,
    ):
        stmt = select(self.model).filter_by(**filter_by).limit(limit).offset(offset)

        if order_by is not None:
            order_field = getattr(self.model, order_by, None)
            if order_field is not None:
                stmt = stmt.order_by(
                    desc(order_field) if order_desc else asc(order_field)
                )

        count_stmt = select(count(self.model.id)).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res_count = await self.session.execute(count_stmt)
        return res.scalars().all(), res_count.scalar_one_or_none()

    async def find_by_id(self, element_id: int | UUID):
        stmt = select(self.model).where(self.model.id == element_id)
        res = await self.session.execute(stmt)
        return res.scalar()

    async def count(self, **filter_by) -> int:
        stmt = select(func.count(self.model.id)).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() or 0

    async def delete(self, element_id: int) -> bool:
        stmt = delete(self.model).filter_by(id=element_id)
        await self.session.execute(stmt)
        return True