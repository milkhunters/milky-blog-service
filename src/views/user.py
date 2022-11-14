from typing import Optional

from pydantic import BaseModel, validator
from tortoise import fields
from models.state import UserStates


class UserResponse(BaseModel):
    """
    Модель пользователя для ответа
    (подробная информация)
    """
    id: int
    username: str
    email: str
    full_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    role_id: int
    state: UserStates


class UserOutResponse(BaseModel):
    """
    Модель пользователя для ответа
    (публичная информация)
    """
    id: int
    username: str
    full_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    role_id: int
    state: UserStates

    @validator("*", pre=True, each_item=False)
    def _tortoise_convert(cls, value):
        """
        Необходимо для преобразования
        некоторых вызываемых полей модели
        и для Reverse и ManyToMany связей

        :param value:
        :return:
        """
        # Вызываемые поля
        if callable(value):
            return value()
        # Конвертирование ManyToManyRelation в список
        if isinstance(value, (fields.ManyToManyRelation, fields.ReverseRelation)):
            return list(value)
        return value

    class Config:
        orm_mode = True
