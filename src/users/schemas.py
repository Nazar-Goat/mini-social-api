from typing import Annotated

from pydantic import  BaseModel,  EmailStr, Field, ConfigDict

class UserRegister(BaseModel):
    first_name: str 
    last_name: str 
    username: str
    email: EmailStr 
    password: str = Field(min_length=8)

    


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
