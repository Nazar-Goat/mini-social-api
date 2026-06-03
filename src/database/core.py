from datetime import datetime
from typing import Annotated

from sqlalchemy import Integer, func
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from src.config import settings


DATABASE_URI = settings.DATABASE_URI

engine = create_async_engine(DATABASE_URI)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# --- Type aliases for common column types ---

int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
# onupdate=func.now() — без лямбд, конвенція компанії
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now())]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa
        return cls.__name__.lower() + "s"