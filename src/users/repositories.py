from sqlalchemy import select

from src.users.models import User
from src.repositories import  SQLRepository


class UserRepository(SQLRepository):
    model = User