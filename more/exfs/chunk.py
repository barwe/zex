import json
import hashlib
from dataclasses import dataclass
from typing import Optional, Tuple, Union
from zex import fs, xdict, xio
from zex.types import RoRecord
from zex.decorators import cache

from .kdefs import *


class Chunk:
    def __init__(
        self,
        fileId: str,
        index: int,
        data: bytes,
        # for tgrpc
        userId: Optional[int] = None,
    ) -> None:
        self.fileId = fileId
        self.index = index
        self.data = data
        self.userId = userId

    @staticmethod
    def split(bytes_data: bytes) -> Tuple[bytes, RoRecord]:
        chunk_meta_size = bytes_data.find(b"\0")
        if chunk_meta_size == -1:
            raise Exception("Chunk meta is not found in mixed frame.")
        chunk_data = bytes_data[chunk_meta_size + 1 :]
        try:
            chunk_meta_str = bytes_data[:chunk_meta_size].decode("utf-8")
            chunk_meta = json.loads(chunk_meta_str)
        except Exception:
            raise Exception("Invalid chunk meta.")
        return chunk_data, chunk_meta

    def validate(self, meta: "FileMeta") -> Union[Tuple[int, str], None]:
        max_index = meta.totalChunks - 1
        if self.index > max_index:
            raise Exception(f"Chunk index {self.index} is out of range (max: {max_index}).")
        if self.index < max_index and len(self.data) != meta.chunkSize:
            raise Exception("Unmatched data length with preset chunk size.")


@dataclass
class ChunkResult:
    next_index: int
    chunk_size: int = None  # 客户端下次应该发送的数据块大小
    checked: bool = False


class FileMeta:
    def __init__(
        self,
        id: str,
        fileSize: int,  # 文件总大小
        chunked: bool,  # 文件是否分片
        chunkSize: int,  # 每个分片的大小 (Bytes)
        totalChunks: int,  # 总分片数
        # 文件完整路径为 /path/to/users/{userId}/{saveAs}
        # userId 根据 userToken 推导
        saveAs: str,
        destServer: Optional[str] = None,  # "tgrpc" | "api"
        tgrpcServerId: Optional[int] = None,  # required for admin
        userToken: str = None,  # on api
        userId: str = None,  # on tgrpc
        overwrite=False,
        extra=None,
        **kwargs,
    ):
        self.id = id
        self.fileId = id
        self.fileSize = fileSize
        self.chunked = chunked
        self.chunkSize = chunkSize
        self.totalChunks = totalChunks
        self.saveAs = saveAs
        self.userToken = userToken
        self.userId = userId
        self.destServer = destServer
        self.tgrpcServerId = tgrpcServerId
        self.overwrite = overwrite
        self.extra = extra or {}

    def dumps(self) -> RoRecord:
        return xdict.pick_keys(self.__dict__, FM_KEYS_DUMPED)

    def json(self) -> RoRecord:
        return xdict.pick_keys(self.__dict__, FM_KEYS_DUMPED)

    def __hash__(self) -> int:
        d = xdict.pick_keys(self.__dict__, FM_KEYS_HASHED)
        fset = frozenset([(k, v) for k, v in d.items()])
        return hash(fset)

    def breakpoint(self, filepath: str):
        """基于文件的大小推断断点恢复索引"""
        if not fs.exists(filepath):
            return 0
        size = fs.getsize(filepath)
        nf = size / self.chunkSize
        ni = int(nf)
        # 不是 chunkSize 的整数倍 & 不是最后一个 chunk
        if nf != ni:
            if ni + 1 != self.totalChunks:
                raise Exception("Invalid breakpoint.")
            return ni + 1
        return ni

    # on api
    async def get_md5_async(self, file_path: str):
        size = fs.getsize(file_path)
        if size != self.fileSize:
            raise Exception(f"文件实际大小与 fileMeta.fileSize 不一致: {size} != {self.fileSize}")

        md5_hash = hashlib.md5()
        import aiofiles  # fmt:skip
        async with aiofiles.open(file_path, "rb") as f:
            while True:
                chunk = await f.read(1024)
                if not chunk:
                    break
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    # on tgrpc
    @staticmethod
    @cache(lambda _: fs.getmtime(_))
    def check_md5(file_path: str):
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @staticmethod
    def from_file(source: str) -> "FileMeta":
        if fs.exists(source):
            data = xio.read_json(source)
            return FileMeta(**data)
        raise FileNotFoundError(source)
