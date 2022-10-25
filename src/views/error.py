"""Application implementation - error response."""
from typing import Dict, Any, Optional, List
from http import HTTPStatus

from pydantic import BaseModel, root_validator


class ErrorModel(BaseModel):
    """Определяет базовую модель ошибки для ответа.
     Атрибуты:
         code (int): код состояния ошибки HTTP.
         message (str): Подробная информация об ошибке HTTP.
         status (str): фраза-причина ошибки HTTP согласно RFC7235. ПРИМЕЧАНИЕ! Установлен
             автоматически на основе кода состояния ошибки HTTP.
     Поднимает:
         pydantic.error_wrappers.ValidationError: если любой из предоставленных атрибутов
             не проходит проверку типа.
    """

    code: int
    message: str
    details: Optional[List[Dict[str, Any]]]

    @root_validator(pre=False, skip_on_failure=True)
    def _set_status(cls, values: dict) -> dict:
        """Устанавливает значение поля состояния на основе значения атрибута кода.
         Аргументы:
             values(dict): хранит атрибуты объекта ErrorModel.
         Возвращает:
             dict: атрибуты объекта ErrorModel с полем состояния.
        """
        values["status"] = HTTPStatus(values["code"]).name
        return values

    class Config:
        """Подкласс конфигурации, необходимый для расширения/переопределения сгенерированной схемы JSON.
         Более подробную информацию можно найти в документации pydantic:
        https://pydantic-docs.helpmanual.io/usage/schema/#schema-customization
        """

        @staticmethod
        def schema_extra(schema: Dict[str, Any]) -> None:
            """Пост-обработка сгенерированной схемы.
             Method может иметь один или два позиционных аргумента.
             Первым будет словарь схемы. Второй, если он будет принят, будет модельным классом. Ожидается, что вызываемый объект изменит словарь схемы на месте; возвращаемое значение не используется.
             Аргументы:
                 схема (typing.Dict[str, typing.Any]): словарь схемы.
             Аргументы:
                 схема (typing.Dict[str, typing.Any]): словарь схемы.
            """
            # Override schema description, by default is taken from docstring.
            schema["description"] = "Error model."
            # Add status to schema properties.
            schema["properties"].update(
                {"status": {"title": "Status", "type": "string"}}
            )
            schema["required"].append("status")


class ErrorResponse(BaseModel):
    """Модель ошибки.
     Атрибуты:
         ошибка (ErrorModel): экземпляр объекта класса ErrorModel.
     Поднимает:
         pydantic.error_wrappers. ValidationError: если любой из предоставленных атрибутов
             не проходит проверку типа.
    """

    error: ErrorModel

    def __init__(self, **kwargs):
        # Аккуратный трюк, чтобы по-прежнему использовать kwargs в модели ErrorResponse.
        super().__init__(error=ErrorModel(**kwargs))

    class Config:

        @staticmethod
        def schema_extra(schema: Dict[str, Any]) -> None:
            schema["description"] = "Error response model."


