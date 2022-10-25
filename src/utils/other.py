import time


def benchmark(func):
    """
    Декоратор, выводящий время, которое заняло
    выполнение декорируемой функции.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        print("---", func.__name__, time.time() - start_time, "seconds ---")
        return res
    return wrapper


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')
