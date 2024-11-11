import time
import threading


def throttle(interval: int):
    """
    限制一个函数在一定时间内只能被调用一次，防止其被过于频繁地调用。
    """

    def decorator(func):

        last_time_called = [0]  # 使用列表以便在嵌套函数中修改
        lock = threading.Lock()

        def wrapper(*args, **kwargs):
            with lock:
                current_time = time.time()
                if current_time - last_time_called[0] >= interval:
                    last_time_called[0] = current_time
                    return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["throttle"]
