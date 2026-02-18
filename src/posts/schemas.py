from pydantic import BaseModel 
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

    from_attributes = True


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    author: AuthorOut
    created_at: datetime
    
