import uuid

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from starlette import status

from . import models
from .database import get_db
from .schemas import auth_schemas

from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
oauth2_scheme_google = OAuth2PasswordBearer(tokenUrl='login/google/callback')

oauth_client = OAuth()
oauth_client.register(
    name="google",
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    client_kwargs={
        'scope': 'openid profile email'
    }
)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(
        {"exp": expire}
    )  # Добавляем новое значение времени исчезновения token
    jwt.expires_at = expire

    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )  # Шифруем токен с помощью указанного алгоритма и по секретному ключу
    return encoded_jwt


async def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_guid, email = payload.get("user_guid"), payload.get("email")

        if user_guid is None or email is None:
            raise credentials_exception
        token_data = auth_schemas.TokenData(guid=uuid.UUID(user_guid), email=email)
    except JWTError as e:
        raise credentials_exception from e

    return token_data


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )  # Создаем описание ошибки для неправильного токена
    return await verify_token(token, credentials_exception)


async def is_current_user_admin(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    admin_role = db.query(models.Role).filter(models.Role.name.in_(["Администратор 💫", "Создатель 🌀"]), models.Role.user_guid == current_user.guid).first()

    if admin_role is None:
        if current_user.email != settings.owner_email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Don't have permissions to perform.")

    return current_user
