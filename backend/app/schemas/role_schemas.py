import uuid
from typing import Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str


class RoleUserOut(RoleBase):
    id: int


class RoleCreate(RoleBase):
    user_guid: Optional[uuid.UUID] = None


class RoleUpdate(BaseModel):
    user_guid: Optional[uuid.UUID] = None
