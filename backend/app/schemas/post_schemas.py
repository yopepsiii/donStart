from datetime import datetime
from pydantic import BaseModel
from ..schemas import user_schemas


class PostBase(BaseModel):
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class PostOut(PostBase):
    id: int
    created_at: datetime
    creator: user_schemas.UserOut

    class Config:
        from_attributes = True
