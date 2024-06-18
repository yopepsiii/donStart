import uuid

from pydantic import BaseModel, conint


class VoteBase(BaseModel):
    pass


class VoteCreate(VoteBase):
    game_guid: uuid.UUID
    type: conint(le=1)
