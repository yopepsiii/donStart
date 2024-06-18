import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from backend.app import models
from backend.app.database import get_db
from backend.app.oauth2 import is_current_user_admin
from backend.app.schemas import role_schemas

router = APIRouter(prefix="/roles", tags=["Roles"])


# Создать новую роль
@router.post('', response_model=role_schemas.RoleUserOut, status_code=status.HTTP_201_CREATED)
async def create_role(role_data: role_schemas.RoleCreate, db: Session = Depends(get_db),
                      current_user: models.User = Depends(is_current_user_admin)):
    if role_data.name == "Администратор 💫":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to perform this action")

    if role_data.user_guid is None:
        user = current_user
    else:
        user = db.query(models.User).filter(models.User.guid == role_data.user_guid).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with UUID {role_data.user_guid} doesn't exist")

    role = models.Role(user_guid=user.guid, name=role_data.name)
    db.add(role)
    db.commit()
    db.refresh(role)

    return role


# Удалить роль
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(id: int, db: Session = Depends(get_db),
                      current_user: models.User = Depends(is_current_user_admin)):
    role = db.query(models.Role).filter(models.Role.id == id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role {id} doesn't exist")
    if role.name == "Администратор 💫":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to perform this action")
    db.delete(role)
    db.commit()

    return


# Изменить роль
@router.patch('/{id}', response_model=role_schemas.RoleUserOut)
async def update_role(id: int, role_updated_data: role_schemas.RoleUpdate, db: Session = Depends(get_db),
                      current_user: models.User = Depends(is_current_user_admin)):
    if role_updated_data.name == "Администратор 💫":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to perform this action")
    role_query = db.query(models.Role).filter(models.Role.id == id)
    role = role_query.first()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {id} doesn't exist",
        )

    if role_updated_data.user_guid is not None:
        potential_user = db.query(models.User).filter(models.User.guid == role_updated_data.user_guid).first()
        if potential_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {role_updated_data.user_guid} doesn't exist",
            )

    to_update = role_updated_data.dict(exclude_unset=True)

    if to_update:
        role_query.update(to_update, synchronize_session=False)
        db.commit()
        db.refresh(role)

    return role
