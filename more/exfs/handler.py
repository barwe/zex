import time
import threading
from typing import IO, ClassVar, Dict, Optional
from zex import fs
from zex.log import logger
from zex.types import RoRecord
from zex.decorators import cache


class FileHandler:
    """Please use `FileHanfler.open()` to get file handler."""

    handlers: ClassVar[Dict[str, "FileHandler"]] = {}

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.descriptor: IO = None
        self.last_used_at: float = None
        self.open_args: RoRecord = None
        self.closing_timer = False

    @cache()
    def __str__(self) -> str:
        return f"FileHandler('{fs.basename(self.file_path)}')"

    def write(self, data):
        if self.descriptor.closed:
            raise Exception(f"{self} is already closed")
        self.last_used_at = time.time()
        self.descriptor.write(data)

    def close(self):
        if self.file_path in self.handlers:
            logger.info(f"{self} is closed")
            self.descriptor.close()
            del self.handlers[self.file_path]

    def set_closing_timer(self, seconds=60):
        """如果一个文件句柄长时间没有使用的话，关闭它"""
        if self.closing_timer:
            raise Exception(f"{self} closing timer is already created")
        thread = threading.Thread(target=self._last_used_watcher, args=(seconds,))
        thread.start()
        self.closing_timer = thread

    def _last_used_watcher(self, secs: int):
        while True:
            if self.descriptor.closed:
                break
            if time.time() - self.last_used_at > secs:
                logger.info(f"{self} is free too long and will be closed")
                self.close()
                break
            time.sleep(10)

    @classmethod
    def create(cls, file_path: str, closing_timer: Optional[int] = None, **open_args: RoRecord) -> "FileHandler":
        fp = fs.abspath(file_path)
        if fp in cls.handlers:
            raise Exception(f"{cls.handlers[fp]} is already created")
        fd = open(fp, **open_args)
        handler = cls(fp)
        handler.descriptor = fd
        handler.last_used_at = time.time()
        handler.open_args = open_args
        cls.handlers[fp] = handler
        if closing_timer and closing_timer > 0:
            handler.set_closing_timer(closing_timer)
        _ = f" with closing timer ({closing_timer} seconds)" if closing_timer else ""
        logger.info(f"{handler} is created{_}")
        return handler

    @classmethod
    def get(cls, file_path: str) -> "FileHandler":
        fp = fs.abspath(file_path)
        if fp not in cls.handlers:
            raise Exception(f"FileHandler('{fs.basename(file_path)}') is not created")
        return cls.handlers[fp]
