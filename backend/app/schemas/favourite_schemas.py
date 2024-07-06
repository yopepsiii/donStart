import uuid

from pydantic import BaseModel


class Favourite(BaseModel):
    game_guid: uuid.UUID
