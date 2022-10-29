from typing import List, Optional
from pydantic import BaseModel, validator
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime

from utils.exceptions import APIError
from ..tables.user import User as UserTable
from utils import validations


class UserBase(BaseModel):
    username: str
    email: str

    @validator('email')
    def email_must_be_valid(cls, value):
        if not validations.is_valid_email(value):
            raise APIError(api_code=902)
        return value

    @validator('username')
    def username_len(cls, value):
        if not validations.is_valid_username(value):
            raise APIError(api_code=901)
        return value


class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_must_be_valid(cls, value):
        if not validations.is_valid_password(value):
            raise APIError(api_code=921)
        return value


class UserAuthentication(BaseModel):
    username: str
    password: str


class User(BaseModel):
    """
    Модель пользователя
    (подробные данные)

    """
    id: int
    username: str
    email: str
    full_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    role_id: int
    state: int  # TODO: перейти на enum
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


class UserUpdate(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class UserDelete(BaseModel):
    id: int
    delete_time: datetime


class UserOut(BaseModel):
    """
    Модель пользователя
    (публичные данные)

    """
    id: int
    role_id: int
    state: int
    username: str
    full_name: str

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
