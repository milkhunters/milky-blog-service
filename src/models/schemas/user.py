from typing import Optional
from pydantic import BaseModel, validator
from tortoise import fields
from datetime import datetime

from exceptions import APIError
from models import UserStates
from utils import validators


class User(BaseModel):
    """
    Модель пользователя

    """
    id: int
    username: str
    email: str
    full_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    role_id: int
    state: UserStates
    create_time: datetime
    update_time: datetime

    @validator("*", pre=True, each_item=False)
    def _tortoise_convert(cls, value):
        # Computed fields
        if callable(value):
            return value()
        # Convert ManyToManyRelation to list
        if isinstance(value, (fields.ManyToManyRelation, fields.ReverseRelation)):
            return list(value)
        return value

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @validator('username')
    def username_must_be_valid(cls, value):
        if not validators.is_valid_username(value):
            raise APIError(api_code=901)
        return value

    @validator('email')
    def email_must_be_valid(cls, value):
        if not validators.is_valid_email(value):
            raise APIError(api_code=902)
        return value

    @validator('password')
    def password_must_be_valid(cls, value):
        if not validators.is_valid_password(value):
            raise APIError(api_code=921)
        return value


class UserAuth(BaseModel):
    username: str
    password: str

    @validator('username')
    def username_must_be_valid(cls, value):
        if not validators.is_valid_username(value):
            raise APIError(api_code=901)
        return value

    @validator('password')
    def password_must_be_valid(cls, value):
        if not validators.is_valid_password(value):
            raise APIError(api_code=921)
        return value


class UserUpdate(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

    @validator('username')
    def username_must_be_valid(cls, value):
        if not validators.is_valid_username(value):
            raise APIError(api_code=901)
        return value


class UserDelete(BaseModel):
    id: int
    delete_time: datetime
