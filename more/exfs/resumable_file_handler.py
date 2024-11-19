# 文件断点续传
import time
import asyncio
import aiofiles
from typing import ClassVar, Dict, IO
from os.path import exists, abspath, dirname, basename
from zex import fs, xio, logger, RoRecord, N
from .chunk import FileMeta
from .kdefs import *


class FileHandlerError(Exception): ...


class AsyncFileHandler:

    handlers: ClassVar[Dict[str, "AsyncFileHandler"]] = {}

    def __init__(self, file_path: str, meta: FileMeta, closing_timer_seconds=60) -> None:
        self.file_path = abspath(file_path)
        self.temp_file_path = self.file_path + ".temp"
        self.temp_meta_path = self.file_path + ".meta"

        self._writer: IO = None
        self.last_used_at: float = None
        self.open_args: RoRecord = None
        self.closing_timer_task = None
        self.closing_timer_seconds = closing_timer_seconds
        self.closed = True

        self.meta: FileMeta = None
        self.next_index: int = None

        self.meta = meta
        self._check_meta()

        # 不允许存在正式文件
        if exists(self.file_path):
            raise FileHandlerError(f"{self} 断点检查时发现正式文件已存在: {self.file_path}")

    def __str__(self) -> str:
        return f"AsyncFileHandler<'{basename(self.file_path)}'>"

    def _check_meta(self):
        # 移除所有存在的正式文件和临时文件
        if self.meta.overwrite:
            fs.rmfiles(self.file_path, self.temp_file_path, self.temp_meta_path)

        # 临时文件：数据文件和元数据文件都存在才能触发续传
        if exists(self.temp_file_path) and exists(self.temp_meta_path):
            temp_meta = FileMeta.from_file(self.temp_meta_path)
            if temp_meta.fileId != self.meta.fileId:
                raise FileHandlerError(f"{self} 断点检查时传入的文件ID与已经完成的临时文件的ID不一致: {self.meta.fileId} != {temp_meta.fileId}")
            try:
                next_index = self.meta.breakpoint(self.temp_file_path)
            except:
                raise FileHandlerError("断点检查时从已完成的临时文件中计算出的断点索引无效")
        else:
            next_index = 0
            # 缺少一个文件时，删除另一个文件
            fs.rmfiles(self.temp_file_path, self.temp_meta_path)
            fs.mkdir(dirname(self.temp_file_path))
            self.meta.extra = {
                K_EXTRA_NAME: basename(self.file_path),
                K_EXTRA_FILE: self.file_path,
                K_EXTRA_TMPFILE: self.temp_file_path,
                K_EXTRA_TMPMETAFILE: self.temp_meta_path,
            }
            xio.write_json(self.meta.json(), self.temp_meta_path)

        self.next_index = next_index
        return next_index

    async def open(self, open_args: N[RoRecord] = None):
        if not self.closed:
            raise FileHandlerError(f"{self} is unclosed.")
        fp = self.temp_file_path
        if fp in self.handlers:
            raise FileHandlerError(f"{self} is opened.")
        open_args = open_args or {}
        open_args["mode"] = open_args.get("mode") or "ab"
        self._writer = await aiofiles.open(fp, **open_args)
        self.closed = False
        self.last_used_at = time.time()
        self.open_args = open_args
        self.handlers[fp] = self._writer
        self.set_closing_timer()
        return self._writer

    async def close(self):
        """关闭打开的文件"""
        if self.temp_file_path in self.handlers:
            logger.info(f"{self} is closed")
            await self._writer.close()
            del self.handlers[self.temp_file_path]
        self.closed = True

    async def write(self, data):
        if self.closed:
            raise FileHandlerError(f"{self} is closed.")
        self.last_used_at = time.time()
        await self._writer.write(data)
        self.next_index += 1

        # 最后一个区块写入成功后
        if self.next_index == self.meta.totalChunks:
            self.complete()

    def complete(self):
        if exists(self.temp_file_path):
            fs.rename(self.temp_file_path, self.file_path)
        fs.rmfiles(self.temp_meta_path)

    def set_closing_timer(self):
        if self.closing_timer_task:
            raise Exception(f"{self} closing timer is already created")

        async def main_coro():
            while True:
                if self.closed:
                    break
                if time.time() - self.last_used_at > self.closing_timer_seconds:
                    logger.info(f"{self} is free too long and will be closed")
                    await self.close()
                    break
                await asyncio.sleep(10)

        self.closing_timer_task = asyncio.create_task(main_coro())

    @staticmethod
    async def create(file_path: str, file_meta: FileMeta, closing_timer=60, open_args=None) -> "AsyncFileHandler":
        """
        - `file_path`: 目标文件路径
        - `file_meta`: FileMeta 对象
        - `closing_timer`: 文件 IO 对象最大空闲时间（秒），超过此时间后文件 IO 对象将会被自动关闭
        - `open_args`: 创建文件 IO 对象需要的参数 (参考 `aiofiles.open()`)
        """
        handler = AsyncFileHandler(file_path, file_meta, closing_timer_seconds=closing_timer)
        await handler.open(open_args=open_args)
        logger.info(f"{handler} is created with closing timer ({handler.closing_timer_seconds} seconds)")
        return handler

    @staticmethod
    def get(file_path: str) -> "AsyncFileHandler":
        fh = AsyncFileHandler(file_path)
        fp = fh.temp_file_path
        if fp not in AsyncFileHandler.handlers:
            del fh
            raise Exception(f"ResumableFileHandler for {basename(file_path)} is not created")
        return AsyncFileHandler.handlers[fp]
