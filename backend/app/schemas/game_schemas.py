import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, validator, field_validator

from backend.app.schemas import user_schemas


class GameBase(BaseModel):
    title: str
    description: str
    img: str


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    img: Optional[str] = None


class GameOut(GameBase):
    guid: uuid.UUID
    creator: user_schemas.UserGamePreview


class GameFullInfo(GameOut):
    created_at: datetime.datetime

    @field_validator('created_at')
    @classmethod
    def trim_date(cls, field: datetime.datetime):
        # Преобразуем значение в дату
        return field.date()


