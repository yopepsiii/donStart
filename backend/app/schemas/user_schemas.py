import datetime
import uuid
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    profile_picture: str


class UserCreate(BaseModel):
    username: str
    profile_picture: Optional[str] = "some picture"  # пофиксить так как в бд тоже такое значение присваиается
    password: str
    email: EmailStr


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(UserBase):
    guid: uuid.UUID
    email: EmailStr
    created_at: datetime.datetime
    roles: List["role_schemas.RoleUserOut"]
    created_games: List["game_schemas.GameUserProfile"]

    class Config:
        from_attributes = True


class UserOut(UserBase):
    guid: uuid.UUID
    roles: List["role_schemas.RoleUserOut"]

    class Config:
        from_attributes = True

class UserGamePreview(UserBase):
    guid: uuid.UUID

    class Config:
        from_attributes = True

from ..schemas import role_schemas, game_schemas
