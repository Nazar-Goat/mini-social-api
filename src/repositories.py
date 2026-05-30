from abc import abstractmethod, ABC

from sqlalchemy import insert, UUID, desc, asc, delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count, func


class AbstractRepository(ABC):
    @abstractmethod
    async def add(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def edit(self, element_id: int | str, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def get(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError


class SQLRepository(AbstractRepository):
    model = None
    relationships = []

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, data: dict) -> int | UUID:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def add_no_return(self, data: dict) -> None:
        stmt = insert(self.model).values(**data)
        await self.session.execute(stmt)

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
        res = res.scalar_one_or_none()
        return res

    async def get_all(self):
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        res = res.scalars().all()
        return res

    async def get_elements(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = res.unique().scalars().all()
        return res

    async def get_field(self, field: str, **filter_by):
        stmt = select(getattr(self.model, field)).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = res.scalar_one_or_none()
        return res

    async def get_with_limit_offset(
        self,
        limit: int,
        offset: int,
        filter_by: dict,
        order_by: str | None = None,
        order_desc: bool = None,
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
        res = res.scalars().all()
        res_count = await self.session.execute(count_stmt)
        res_count = res_count.scalar_one_or_none()
        return res, res_count

    async def find_by_id(self, element_id: int | UUID):
        stmt = select(self.model).where(self.model.id == element_id)
        res = await self.session.execute(stmt)
        res = res.scalar()
        return res

    async def count(self, filter_by):
        stmt = select(func.count(self.model.id)).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = res.scalar_one_or_none()
        return res

    async def delete(self, element_id):
        stmt = delete(self.model).filter_by(id=element_id)
        res = await self.session.execute(stmt)
        return True

    async def soft_delete(self, element_id):
        stmt = (
            update(self.model)
            .where(
                self.model.id == element_id,
                self.model.deleted_at.is_(None),
            )
            .values(deleted_at=func.now())
            .returning(self.model.id)
        )

        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_with_soft_deleted(self, **filters):
        stmt = (
            select(self.model)
            .execution_options(include_deleted=False)
            .filter_by(**filters)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
