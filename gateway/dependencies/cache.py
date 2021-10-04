import functools
from asyncio import Lock
from typing import Optional

from cachetools import Cache, TTLCache, cached
from cachetools.keys import hashkey
from fastapi import Depends

from gateway.settings import Settings, get_settings


@cached({}, key=lambda settings: (settings.GRPC_CACHE_ENABLED,
                                  settings.GRPC_CACHE_MAX_SIZE,
                                  settings.GRPC_CACHE_TTL))
def grpc_cache(settings: Settings = Depends(get_settings)) -> Optional[Cache]:
    if not settings.GRPC_CACHE_ENABLED:
        return None
    return TTLCache(maxsize=settings.GRPC_CACHE_MAX_SIZE, ttl=settings.GRPC_CACHE_TTL)


async def grpc_cache_lock():
    def get_lock(lock=Lock()):
        return lock
    return get_lock()


def aio_cachedmethod(cache, lock, key=hashkey):
    def decorator(method):
        async def wrapper(self, *args, **kwargs):
            c = cache(self)
            if c is None:
                return await method(self, *args, **kwargs)
            k = key(method.__name__, *args, **kwargs)
            try:
                async with lock(self):
                    return c[k]
            except KeyError:
                pass
            v = await method(self, *args, **kwargs)
            try:
                async with lock(self):
                    return c.setdefault(k, v)
            except ValueError:
                return v
        return functools.update_wrapper(wrapper, method)
    return decorator
