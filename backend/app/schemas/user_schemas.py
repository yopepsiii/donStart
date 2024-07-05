import datetime
import uuid
from typing import Optional, List

from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    username: constr(min_length=2, max_length=20)
    profile_picture: str


class UserCreate(BaseModel):
    username: constr(min_length=2, max_length=20)
    profile_picture: Optional[str] = "user_profile_default"
    password: constr(min_length=7)
    email: EmailStr


class UserUpdate(BaseModel):
    username: Optional[constr(min_length=2, max_length=20)] = None
    password: Optional[constr(min_length=7)] = None
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
