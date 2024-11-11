import time
import inspect
from functools import wraps


def cache(key_fn=None):
    """
    缓存函数的结果，支持自定义缓存键。
    """
    if key_fn is None:
        key_fn = lambda *args, **_: args

    def decorator(func):
        cached_dct = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = key_fn(*args, **kwargs)
            if key in cached_dct:
                return cached_dct[key]
            value = func(*args, **kwargs)
            cached_dct[key] = value
            return value

        return wrapper

    return decorator


def cache_async(key_fn=None):
    """
    缓存异步函数的结果，支持自定义缓存键。
    """
    if key_fn is None:
        key_fn = lambda *args, **_: args

    def decorator(func):
        cached_dct = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(key_fn):
                key = await key_fn(*args, **kwargs)
            else:
                key = key_fn(*args, **kwargs)
            if key in cached_dct:
                return cached_dct[key]
            value = await func(*args, **kwargs)
            cached_dct[key] = value
            return value

        return wrapper

    return decorator


def ttl_cache(ttl: float, key_fn=None):
    """
    缓存函数的结果，支持设置过期时间，支持自定义缓存键。
    """
    if key_fn is None:
        key_fn = lambda *args, **_: args

    def decorator(func):
        cached_dct = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = key_fn(*args, **kwargs)
            current_time = time.time()
            if key in cached_dct:
                value, timestamp = cached_dct[key]
                if current_time - timestamp < ttl:
                    return value
                else:
                    del cached_dct[key]
            value = func(*args, **kwargs)
            cached_dct[key] = (value, current_time)
            return value

        return wrapper

    return decorator


def ttl_cache_async(ttl: float, key_fn=None):
    """
    缓存异步函数的结果，支持设置过期时间，支持自定义缓存键。
    """
    if key_fn is None:
        key_fn = lambda *args, **_: args

    def decorator(func):
        cached_dct = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(key_fn):
                key = await key_fn(*args, **kwargs)
            else:
                key = key_fn(*args, **kwargs)
            current_time = time.time()
            if key in cached_dct:
                value, timestamp = cached_dct[key]
                if current_time - timestamp < ttl:
                    return value
                else:
                    del cached_dct[key]
            value = await func(*args, **kwargs)
            cached_dct[key] = (value, current_time)
            return value

        return wrapper

    return decorator


__all__ = [
    "cache",
    "cache_async",
    "ttl_cache",
    "ttl_cache_async",
]
