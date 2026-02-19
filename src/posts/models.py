from src.database.core import Base

from sqlalchemy import  ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Post(Base):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str]  = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )

    author: Mapped["User"] = relationship("User", back_populates="posts") # type: ignore
    
