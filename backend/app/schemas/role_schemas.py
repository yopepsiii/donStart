import uuid
from typing import Optional

from pydantic import BaseModel, constr


class RoleBase(BaseModel):
    name: constr(min_length=1, max_length=20)
    color: str


class RoleOut(RoleBase):
    id: int
    user_guid: uuid.UUID


class RoleUserOut(RoleBase):
    id: int


class RoleCreate(RoleBase):
    user_guid: Optional[uuid.UUID] = None


class RoleUpdate(BaseModel):
    user_guid: Optional[uuid.UUID] = None
    name: Optional[constr(min_length=1, max_length=20)] = None
    color: Optional[str] = None
