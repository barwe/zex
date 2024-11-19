import os
import inspect
import functools
from zex.log import logger


def get_frame(stacklevel: int):
    """
    1 表示获取此函数的调用者，2 表示获取此函数的调用者的调用者，以此类推。
    - `stacklevel`: 相对调用的位置
    """
    if stacklevel == 1:
        return inspect.currentframe().f_back.f_back
    elif stacklevel == 2:
        return inspect.currentframe().f_back.f_back.f_back
    frame = inspect.currentframe().f_back
    for _ in range(stacklevel):
        frame = frame.f_back
    return frame


def get_call_info(stacklevel: int):
    frame = get_frame(stacklevel + 1)
    code_context = frame.f_code
    filename = code_context.co_filename
    filename = os.path.relpath(filename, os.getcwd())
    lineno = frame.f_lineno
    return filename, lineno


def deprecated(message=None):

    if message is None:
        message = lambda name, **_: f"'{name}' is deprecated and will be removed in future versions."

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            filename, lineno = get_call_info(1)
            msg = message(name=func.__name__, func=func)
            msg = f"{filename}:{lineno} {msg}"
            logger.warning(msg)
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["deprecated"]
