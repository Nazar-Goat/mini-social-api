from src.database.core import Base

from sqlalchemy import  ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Like(Base):
    __tablename__ = "likes"

    post_id = mapped_column(ForeignKey("posts.id"), index=True, nullable=False)
    user_id = mapped_column(ForeignKey("users.id"), index=True, nullable=False)


    post: Mapped["Post"] = relationship("Post", back_populates="likes") # type: ignore
    user: Mapped["User"] = relationship("User", back_populates="likes") # type: ignore

    