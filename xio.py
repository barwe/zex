import os
import sys
import json
from os.path import exists
from .types import Union, T

json_load = json.load
json_loads = json.loads
json_dump = json.dumps
json_dumps = json.dumps


def read(filepath: str):
    with open(filepath) as fr:
        return fr.read()


def write(content: Union[bytes, str], filepath: str, mode=None):
    mode = mode or ("wb" if isinstance(content, bytes) else "w")
    with open(filepath, mode) as fw:
        fw.write(content)


def read_json(filepath: str, default=None):
    if not exists(filepath):
        return default
    with open(filepath) as fr:
        return json.load(fr)


def write_json(data: T, filepath: str, **options):
    with open(filepath, "w") as fw:
        json.dump(data, fw, **options)


def calculate_md5(file_path: str):
    import hashlib

    # 创建一个 MD5 哈希对象
    md5_hash = hashlib.md5()

    # 以二进制模式打开文件
    with open(file_path, "rb") as f:
        # 逐块读取文件内容并更新哈希对象
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)

    # 返回 MD5 哈希值的十六进制表示
    return md5_hash.hexdigest()
