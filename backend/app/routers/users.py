import uuid
from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter, Response
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette import status

from .. import models, utils, oauth2
from ..schemas import user_schemas
from ..database import get_db
from ..utils import validate, validate_list

router = APIRouter(tags=["Users"], prefix="/users")


# Получить всех пользователей
@router.get("", response_model=list[user_schemas.UserOut])
@cache(expire=60 * 60, namespace="users")
async def get_users(response: Response, db: Session = Depends(get_db), skip: int = 0, limit: int = 20, search: Optional[str] = ""):
    users = db.query(models.User).filter((func.lower(models.User.username + models.User.email)).contains(search.lower())).limit(limit).offset(skip)
    users_total_count = db.query(models.User).filter((func.lower(models.User.username + models.User.email)).contains(search.lower())).count()
    response.headers["x-total-count"] = str(users_total_count)
    return validate_list(values=users, class_type=user_schemas.UserOut)

# Получить пользователя по ID
@router.get("/{guid}", response_model=user_schemas.UserProfile)
@cache(expire=60 * 60, namespace="user_by_guid")
async def get_user(guid: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.guid == guid).first()  # type: ignore
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {guid} doesn't exist"
        )
    print(user.favourite_games)
    return validate(value=user, class_type=user_schemas.UserProfile)


# Создать нового пользователя
@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserProfile
)
async def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await FastAPICache.clear()

    return new_user


# Изменить информацию о пользователе
@router.patch("/{guid}", response_model=user_schemas.UserProfile)
async def update_user(
        guid: uuid.UUID,
        updated_data: user_schemas.UserUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
):
    user_query = db.query(models.User).filter(models.User.guid == guid)  # type: ignore
    user = user_query.first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {guid} doesn't exist",
        )
    if user.guid != current_user.guid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to update user with ID {guid}",
        )

    if updated_data.dict().get("password") is not None:
        updated_data.password = utils.hash(updated_data.password)

    update_data = updated_data.dict(exclude_unset=True)

    # Обновить пользователя только с этими полями
    if update_data:
        user_query.update(update_data, synchronize_session=False)
        db.commit()
        db.refresh(user)

        await FastAPICache.clear()

    return user
