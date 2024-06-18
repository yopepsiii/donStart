import uuid

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from .. import models, utils, oauth2
from ..schemas import user_schemas
from ..database import get_db

router = APIRouter(tags=["Users"], prefix="/users")


# Получить всех пользователей
@router.get("", response_model=list[user_schemas.UserOut])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


# Получить пользователя по ID
@router.get("/{guid}", response_model=user_schemas.UserProfile)
async def get_user(guid: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.guid == guid).first()  # type: ignore
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {guid} doesn't exist"
        )
    return user


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

    return user
