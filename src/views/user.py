from pydantic import BaseModel, validator
from tortoise import fields
from models.schemas import User


class UserResponse(User):
    pass


class UserOutResponse(BaseModel):

    id: int
    role_id: int
    state_id: int
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
