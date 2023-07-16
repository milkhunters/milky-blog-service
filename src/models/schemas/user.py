import uuid

from pydantic import BaseModel, validator
from datetime import datetime

from src.models.state import UserState


class User(BaseModel):
    """
    Модель пользователя

    """
    id: uuid.UUID
    username: str
    email: str
    first_name: str = None
    last_name: str = None
    role_id: int
    state: UserState

    created_at: datetime
    updated_at: datetime = None

    class Config:
        from_attributes = True


class UserSmall(BaseModel):
    id: uuid.UUID
    username: str
    first_name: str | None
    last_name: str | None
    role_id: int
    state: UserState

    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    # @validator('username')
    # def username_must_be_valid(cls, value):
    #     if not validators.is_valid_username(value):
    #         raise APIError(api_code=901)
    #     return value
    #
    # @validator('email')
    # def email_must_be_valid(cls, value):
    #     if not validators.is_valid_email(value):
    #         raise APIError(api_code=902)
    #     return value
    #
    # @validator('password')
    # def password_must_be_valid(cls, value):
    #     if not validators.is_valid_password(value):
    #         raise APIError(api_code=921)
    #     return value


class UserAuth(BaseModel):
    username: str
    password: str

    # @validator('username')
    # def username_must_be_valid(cls, value):
    #     if not validators.is_valid_username(value):
    #         raise APIError(api_code=901)
    #     return value
    #
    # @validator('password')
    # def password_must_be_valid(cls, value):
    #     if not validators.is_valid_password(value):
    #         raise APIError(api_code=921)
    #     return value


class UserUpdate(BaseModel):
    username: str = None
    first_name: str = None
    last_name: str = None

    # @validator('username')
    # def username_must_be_valid(cls, value):
    #     if not validators.is_valid_username(value):
    #         raise APIError(api_code=901)
    #     return value


class UserUpdateByAdmin(UserUpdate):
    email: str = None
    role_id: int = None
    state: UserState = None

    # @validator('email')
    # def email_must_be_valid(cls, value):
    #     if not validators.is_valid_email(value):
    #         raise APIError(api_code=902)
    #     return value

    # @validator('role_id')
    # def role_id_must_be_valid(cls, value):
    #     if not validators.is_valid_role_id(value):
    #         raise APIError(api_code=911)
    #     return value
