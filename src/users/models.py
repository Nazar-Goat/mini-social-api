from sqlalchemy.orm import Mapped, mapped_column
from src.database.core import Base, int_pk, created_at, updated_at, str_uniq, str_null_true

class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]