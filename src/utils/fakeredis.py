

class FakeRedisPool:

    def __init__(self, *args, **kwargs):
        self._storage = dict()

    async def close(self, *args, **kwargs):
        pass

    async def ping(self, *args, **kwargs) -> bool:
        return True

    async def set(self, name: any, value: any, **kwargs):
        self._storage[name] = value

    async def get(self, name: any, **kwargs):
        return self._storage.get(name)

    async def expire(self, name: any, expire: int, **kwargs):
        pass

    async def rpush(self, name: any, value: any, **kwargs):
        self._storage[name].append(value)

    async def exists(self, name: any, **kwargs):
        return name in self._storage

    async def lrange(self, name: any, start: int, end: int, **kwargs):
        return self._storage[name][start:end]

    async def delete(self, name: any, **kwargs):
        del self._storage[name]
