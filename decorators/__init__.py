from ._cache import *
from ._throttle import *
from ._deprecated import *


class Singleton:
    __singleton_instance__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__singleton_instance__ is None:
            cls.__singleton_instance__ = super().__new__(cls)
        return cls.__singleton_instance__
