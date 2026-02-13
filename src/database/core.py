from sqlalchemy.ext.asyncio import AsyncAttrs, async_session_maker, create_async_engine

from datetime import datetime
from typing import Annotated

from sqlalchemy import Integer, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from config import get_settings

settings = get_settings()

DATABASE_URI = settings.DATABASE_URI

#create async engine for database connection
engine = create_async_engine(DATABASE_URI)
#create async session fabric  for database sessions
async_session_maker = async_session_maker(engine, expire_on_commit=False)

# annotation constants for common column types
int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True #abstract class , so will not be created as table in database 



    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

