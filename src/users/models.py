from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.core import Base, str_uniq
from src.likes.models import Like

if TYPE_CHECKING:
    from src.posts.models import Post

class User(Base):
    __tablename__ = "users"
    
    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]
    
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    likes: Mapped[list["Like"]] = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan"
    )