from passlib.context import CryptContext
import redis
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def validate_list(values, class_type):
    return [class_type.model_validate(obj) for obj in values]


def validate(value, class_type):
    return class_type.model_validate(value)
