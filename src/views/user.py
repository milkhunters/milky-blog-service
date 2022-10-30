from pydantic import BaseModel, validator
from tortoise import fields
from models.schemas import User


class UserResponse(User):
    """
    Модель пользователя для ответа
    (подробная информация)
    """
    pass


class UserOutResponse(BaseModel):
    """
    Модель пользователя для ответа
    (публичная информация)
    """
    id: int
    role_id: int
    state: int  # TODO: перейти на enum
    username: str
    full_name: str

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
