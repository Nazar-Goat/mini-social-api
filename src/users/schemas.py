from typing import Annotated

from pydantic import  BaseModel,  EmailStr, Field, ValidationError

class UserRegister(BaseModel):
    first_name: str 
    last_name: str 
    username: str
    email: EmailStr 
    password: str = Field(min_length=8)

    class Config:
        extra = "forbid"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
