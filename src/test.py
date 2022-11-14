from typing import TypeVar, Generic


T = TypeVar('T')


class Base(Generic[T]):
    table = T

    def get(self) -> T:
        return self.table


class Some(Base[str]):
    table = str

    def get_type(self):
        return self.table


print(Some().get())  # out: ~T
