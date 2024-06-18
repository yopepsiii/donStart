import uuid

from pydantic import BaseModel


class VoteBase(BaseModel):
    pass


class VoteCreate(VoteBase):
    user_guid: uuid.UUID
    game_guid: uuid.UUID
    type: int
