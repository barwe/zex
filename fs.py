import os
import re
import shutil
from os.path import *
from os.path import __all__ as __os_path__
from typing import Sequence

__all__ = [
    *__os_path__,
    "filename",
    "extname",
    "format_size",
    "mkdir",
    "joinx",
    "numberize_size",
    "rmfile",
    "rmdir",
    "make_slink",
    "make_hlink",
    "listdir",
    "move",
    "copy_dir",
    "copy_file",
    "rename",
    "rmfiles",
    "list_files",
    "get_os_app_data_dir",
]


def format_size(nbytes: int, sep=" "):
    import math

    v = lambda n, u: f"{n}{sep}{u}"
    if nbytes == 0:
        return v(0, "B")
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(nbytes, 1024)))
    p = math.pow(1024, i)
    s = str(round(nbytes / p, 2))
    if s.endswith(".0"):
        s = s[:-2]
    return v(s, size_name[i])


def mkdir(*paths, is_file=False) -> str:
    path = join(*paths)
    if is_file:
        _path = dirname(path)
    else:
        _path = path
    if not exists(_path):
        os.makedirs(_path)
    return path


def joinx(s: str, *a: Sequence[str], create=False, create_parent=False) -> str:
    """`os.path.join` 的强化版本，支持同时创建目标路径，或者创建目标路径的父目录"""
    v = join(s, *a)
    if create:
        if not exists(v):
            os.makedirs(v)
    elif create_parent:
        _v = dirname(v)
        if not exists(_v):
            os.makedirs(_v)
    return v


def numberize_size(hrf_size: str, base=1024):
    """将人类阅读友好的文件大小字符串转换成字节数"""
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    if m := re.match(r"(\d+)\s*(\w?B)", hrf_size):
        n = float(m.group(1))
        i = size_name.index(m.group(2))
        return int(n * pow(base, i))
    raise ValueError(hrf_size)


rmfile = os.remove
rmdir = shutil.rmtree
make_slink = os.symlink
make_hlink = os.link
listdir = os.listdir
move = shutil.move
copy_dir = shutil.copytree
copy_file = shutil.copy


def split_basename(filepath: str):
    "从文件路径的 basename 中拆分出 (filename, extname)"
    _base = basename(filepath)
    if "." not in filepath:
        return (_base, None)
    else:
        arr = _base[::-1].split(".", 1)
        return (arr[1][::-1], arr[0][::-1])


def filename(fp: str):
    """文件名：从文件 basename 中移除了文件扩展名"""
    return split_basename(fp)[0]


def extname(fp: str):
    "文件扩展名：最后一个句号后面的内容；没有句号时返回 None"
    return split_basename(fp)[1]


def rename(_old: str, _new: str):
    x = abspath(_old)
    y = abspath(_new)
    if x != y:
        os.rename(x, y)


def rmfiles(*fps: Sequence[str]):
    for fp in fps:
        if exists(fp):
            os.remove(fp)


def list_files(target_dir: str, pattern: str, exclude_dirs: Sequence[str] = None):
    import re

    items = []
    index = 0
    exclude_dir_set = set(exclude_dirs or [])
    for dp, _, fns in os.walk(target_dir):
        dp_n = os.path.basename(dp)
        if dp_n in exclude_dir_set:
            continue
        for fn in fns:
            if mt := re.match(pattern, fn):
                item = {"id": index, "fn": fn, "dp": dp, "mt": mt.groups()}
                items.append(item)
                index += 1
    return items


def get_os_app_data_dir(*subs: Sequence[str]):
    import platform

    system = platform.system()
    if system == "Windows":
        path_to_appdata = os.getenv("APPDATA")
        target = path_to_appdata if path_to_appdata else None
    else:
        result = join(expanduser("~"), ".config")
        if exists(result):
            target = result
        else:
            target = join(expanduser("~"), ".local", "share")
    if len(subs) > 0:
        target = join(target, *subs)
    return target


def open_dir_explorer(path: str):
    os.system(f"start explorer {path}")
