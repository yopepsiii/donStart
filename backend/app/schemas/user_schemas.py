from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    password: str
    email: EmailStr
    image: Optional[str] = "img"


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
    image: Optional[str] = "img"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserOut(BaseModel):
    image: str
    username: str
    id: int
