import uuid
from typing import Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    color: str


class RoleUserOut(RoleBase):
    id: int
    user_guid: uuid.UUID


class RoleCreate(RoleBase):
    user_guid: Optional[uuid.UUID] = None


class RoleUpdate(BaseModel):
    user_guid: Optional[uuid.UUID] = None
    name: Optional[str] = None
    color: Optional[str] = None
