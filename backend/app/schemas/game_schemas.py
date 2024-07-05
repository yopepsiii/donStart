import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, validator, field_validator, constr

from ..schemas import user_schemas


class GameBase(BaseModel):
    title: constr(min_length=1, max_length=130)
    description: constr(max_length=15000)
    img: str


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=130)] = None
    description: Optional[constr(max_length=15000)] = None
    img: Optional[str] = None


class GameOut(GameBase):
    guid: uuid.UUID
    creator: user_schemas.UserGamePreview
    likes_count: int
    dislikes_count: int

    class Config:
        from_attributes = True


class GameUserProfile(GameBase):
    guid: uuid.UUID
    likes_count: int
    dislikes_count: int

    class Config:
        from_attributes = True


class GameFullInfo(GameOut):
    created_at: datetime.datetime

    class Config:
        from_attributes = True

    @field_validator('created_at')
    @classmethod
    def trim_date(cls, field: datetime.datetime):
        # Преобразуем значение в дату
        return field.date()
