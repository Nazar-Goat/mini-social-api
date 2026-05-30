from pydantic import BaseModel, ConfigDict 
from datetime import datetime

class PostCreate(BaseModel):
    title: str 
    content: str
    

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None 


class AuthorOut(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    author: AuthorOut
    likes_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
