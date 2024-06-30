from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import roles
from starlette import status

from .. import models
from ..config import settings
from ..database import get_db
from ..oauth2 import is_current_user_admin
from ..schemas import role_schemas

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=role_schemas.RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role(new_role_data: role_schemas.RoleCreate, db: Session = Depends(get_db),
                      current_user: models.User = Depends(is_current_user_admin)):
    if new_role_data.name in ["Администратор 💫", "Создатель 🌀"] and current_user.email != settings.owner_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to add role with such name.")

    user_for_role = db.query(models.User).filter(models.User.guid == new_role_data.user_guid).first()

    if user_for_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {new_role_data.user_guid} does not exist.")

    new_role = models.Role(**new_role_data.dict())

    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return new_role


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(id: int, db: Session = Depends(get_db),
                      current_user: models.User = Depends(is_current_user_admin)):
    role = await check_role(id, current_user, db)

    db.delete(role)
    db.commit()

    return {"message": "Sucessfuly deleted"}


@router.patch("/{id}", response_model=role_schemas.RoleOut)
async def update_role(id: int, updated_role_data: role_schemas.RoleUpdate, db: Session = Depends(get_db),
                      current_user: models.User = Depends(is_current_user_admin)):
    role, role_query = await check_role(id, current_user, db, get_query=True)

    if updated_role_data.name in ["Администратор 💫", "Создатель 🌀"] and current_user.email != settings.owner_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to update role name with such name.")

    if updated_role_data.user_guid is not None:
        potential_user = db.query(models.User).filter(models.User.guid == updated_role_data.user_guid).first()

        if potential_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User {updated_role_data.user_guid} does not exist.")

    updated_data = updated_role_data.dict(exclude_unset=True)

    if updated_data:
        role_query.update(updated_data)
        db.commit()
        db.refresh(role)

    return role


async def check_role(id: int, current_user, db, get_query=False):
    role_query = db.query(models.Role).filter(models.Role.id == id)
    role = role_query.first()

    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role {id} does not exist.")

    if role.name in ["Администратор 💫", "Создатель 🌀"] and current_user.email != settings.owner_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You have not allowed to delete this role.")

    if get_query:
        return role, role_query
    else:
        return role

# надо добавить возможность добавить цвет роли

# админ при выдачи роли будет выбирать из списка всех пользователей платформы, кроме создателей
# | не будет варианта не выбрать пользователя
# | можно будет меня название роли и ничего более
# | можно будет менять владельца роли и ничего более
# + возможность выбрать цвет роли (хз в чем)
# / поменять архитектуру на многие-ко-многим (присваивание ролей, а не создание новых)
