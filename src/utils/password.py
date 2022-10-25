import hashlib
import random

from .other import int_to_bytes


def get_hashed_password(password: str) -> str:
    """
    Генерирует хеш пароля со случайной солью
    Соль состоит из 5 символов и записывается
    справа от хеша. Хеш, в свою очередь, записывается
    в хекс-формате.

    :param password: soult + hashed_pass str
    :return:
    """
    salt = random.randint(10000, 19000)
    hashed_pass = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), int_to_bytes(salt), 50000, dklen=32).hex()
    storage = str(salt) + hashed_pass
    return storage


def verify_password(password: str, storage: str) -> bool:
    """
    Проверяет пароль на валидность
    :param password:
    :param storage: salt + hashed_pass str from db
    :return:
    """
    salt = int(storage[:5])
    hashed_pass_from_storage = storage[5:]
    new_hash_pass = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), int_to_bytes(salt), 50000, dklen=32).hex()
    return new_hash_pass == hashed_pass_from_storage
