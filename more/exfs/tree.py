import os
import stat
from zex import fs
from zex.decorators import ttl_cache
from typing import Mapping, Optional, Sequence
from typing import Any, List, Dict

as_ms = lambda x: int(x * 1000)
get_ctime = lambda s: as_ms(os.path.getctime(s))
get_mtime = lambda s: as_ms(os.path.getmtime(s))
get_mod = lambda s: stat.filemode(os.stat(s).st_mode)
get_size_bytes = lambda s: os.path.getsize(s)

TreeNodeInfo = Mapping[str, Any]


sort_by_name = lambda arr: sorted(arr, key=lambda x: x["name"])


class K_FTYPE:
    FILE = "file"
    DIR = "dir"
    UNKNOWN = "unknown"


class TreeNode:
    CACHED_NODES: Dict[str, "TreeNode"] = {}
    K_FTYPE = K_FTYPE

    def __init__(self, path: str, depth: Optional[int] = None):
        self.path = path
        self.depth = depth
        self.children: List["TreeNode"] = []

    def __hash__(self) -> int:
        return hash(self.path)

    @property
    def ftype(self):
        if fs.isfile(self.path):
            return K_FTYPE.FILE
        elif fs.isdir(self.path):
            return K_FTYPE.DIR
        return K_FTYPE.UNKNOWN

    def add_child(self, other: "TreeNode"):
        if other not in self.children:
            self.children.append(other)

    @ttl_cache(10, lambda _self, reroot=None: (_self.path, reroot))
    def base_info(self, reroot: Optional[str] = None) -> Mapping[str, Any]:
        d = {
            "name": fs.basename(self.path),
            "type": self.ftype,
            "ctime": get_ctime(self.path),
            "mtime": get_mtime(self.path),
            "mod": get_mod(self.path),
        }
        if reroot != None:
            v = fs.relpath(self.path, reroot)
            d["path"] = "" if v == "." else v
        if self.ftype == K_FTYPE.FILE:
            d["size_bytes"] = size = get_size_bytes(self.path)
            d["size"] = fs.format_size(size)
        return d

    def json(self, reroot: Optional[str] = None, depth=None) -> TreeNodeInfo:
        if not fs.exists(self.path):
            return None
        d = {**self.base_info(reroot=reroot)}
        if self.ftype == K_FTYPE.DIR and (dep := depth if depth != None else self.depth) > 0:
            f_s, d_s, e_s = [], [], []
            for o in self.children:
                if a := o.json(reroot, dep - 1):
                    if o.ftype == "file":
                        f_s.append(a)
                    elif o.ftype == "dir":
                        d_s.append(a)
                    else:
                        e_s.append(a)
            d["children"] = [*sort_by_name(d_s), *sort_by_name(f_s), *sort_by_name(e_s)]
        return d

    @staticmethod
    def get(a: str, *arr: Sequence[str], depth: Optional[int] = None) -> "TreeNode":
        abs_path = fs.abspath(fs.join(a, *arr))
        if abs_path not in TreeNode.CACHED_NODES:
            node = TreeNode(path=abs_path, depth=depth)
            TreeNode.CACHED_NODES[abs_path] = node
        else:
            node = TreeNode.CACHED_NODES[abs_path]
            if depth:
                node.depth = depth
        return node

    @staticmethod
    def info(a: str, *arr: Sequence[str], reroot: Optional[str] = None):
        node: "TreeNode" = TreeNode.get(a, *arr)
        return node.json(reroot=reroot, depth=0)
