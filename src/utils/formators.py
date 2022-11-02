import re


def slugify(string: str) -> str:
    """
    Функция для преобразования строки в слаг

    :param string:
    :return:
    """
    string = string.lower().strip()
    string = re.sub(r'[^\w\s-]', '', string)
    string = re.sub(r'[\s_-]+', '-', string)
    string = re.sub(r'^-+|-+$', '', string)
    return string


def tokenize(string: str) -> list[str]:
    """
    Функция для токенизации строки

    :param string:
    :return:
    """
    string = string.lower().strip()
    string = re.sub(r'[^\w\s-]', '', string)
    string = re.sub(r'[\s_-]+', ' ', string)
    string = re.sub(r'^-+|-+$', '', string)
    return string.split()
