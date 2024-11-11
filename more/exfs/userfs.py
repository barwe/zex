from dataclasses import dataclass
from typing import Optional, Mapping, Sequence, Any
from zex import fs, xio
from .tree import TreeNode


@dataclass
class Target:
    source: str
    dest: Optional[str] = None
    type: Optional[str] = None  # make
    depth: Optional[int] = None  # list


ReturnData_T = Mapping[str, Any]


class RD:

    @staticmethod
    def success(data=None) -> ReturnData_T:
        return {"success": True, "data": data}

    @staticmethod
    def failed(message_or_exception) -> ReturnData_T:
        return {"success": False, "message": str(message_or_exception)}


def list_with_depth(paths: Sequence[str], depth: int, ignores: Sequence[str] = None, **_):

    if ignores and len(ignores) > 0:
        ignore = lambda p: fs.path_matches_patterns(p, ignores)
    else:
        ignore = lambda _: False

    def list_one(root_dir: str):

        def recurse(ps: Sequence[str], dep: int):
            if dep <= 0:
                return [TreeNode.get(i, depth=0) for i in ps]

            nodes = []
            for path0 in ps:
                node0 = TreeNode.get(path0, depth=dep)
                nodes.append(node0)
                if not fs.isdir(path0):
                    continue
                next_ps = []
                for name in fs.listdir(path0):
                    path1 = fs.join(path0, name)
                    if ignore(path1):
                        continue
                    node = TreeNode.get(path1, depth=dep - 1)
                    node0.add_child(node)
                    if fs.isdir(path1):
                        next_ps.append(path1)
                recurse(next_ps, dep - 1)

            return nodes

        return recurse([root_dir], depth)[0]

    return [list_one(r) for r in paths]


class LocalUserFileManager:
    def __init__(self, user_dir: str) -> None:
        self.user_dir = fs.mkdir(user_dir)

    def get_and_check(self, target: str):
        abs_path: str = fs.abspath(f"{self.user_dir}/{target}")
        if not abs_path.startswith(self.user_dir):
            raise Exception(f"No permission to delete file out of your space.")
        return abs_path

    def __call__(self, action: str, targets):
        fn = getattr(self, action)
        return [fn(Target(**td)) for td in targets]

    def rename(self, target: Target):
        try:
            old_path = self.get_and_check(target.source)
            new_path = fs.join(fs.dirname(old_path), fs.basename(target.dest))
            fs.rename(old_path, new_path)
            data = TreeNode.info(new_path, reroot=self.user_dir)
            return RD.success(data)
        except FileNotFoundError:
            return RD.failed(f"Source path not found: {target.source}")
        except OSError as e:
            if "Directory not empty" in str(e):
                return RD.failed(f"Dest path exists: {target.dest}")
            raise
        except Exception as e:
            return RD.failed(e)

    def delete(self, target: Target):
        try:
            abs_path = self.get_and_check(target.source)
            if abs_path == self.user_dir:
                return RD.failed(f"Cannot remove the path: {target.source}")
            if not fs.exists(abs_path):
                return RD.success(None)
            if fs.isfile(abs_path):
                fs.rmfile(abs_path)
            elif fs.isdir(abs_path):
                fs.rmdir(abs_path)
            else:
                return RD.failed(f"Cannot remove the path: {target.source} (upsupported file type)")
            return RD.success(None)
        except FileNotFoundError:
            return RD.failed(f"Path not found: {target.source}")
        except Exception as e:
            return RD.failed(e)

    def list(self, target: Target):
        max_depth = target.depth or 0
        try:
            full_path = self.get_and_check(target.source)
            root_node = list_with_depth([full_path], max_depth)[0]
            data = root_node.json(self.user_dir, depth=max_depth)
            return RD.success(data)
        except FileNotFoundError:
            return RD.failed(f"Path not found: {target.source}")
        except Exception as e:
            return RD.failed(e)

    def make(self, target: Target):
        try:
            abs_path = self.get_and_check(target.source)
            if fs.exists(abs_path):
                return RD.failed(f"Path exists: {target.source}")
            if target.type == "file":
                fs.mkdir(fs.dirname(abs_path))
                with open(abs_path, "w") as f:
                    f.write("")
            elif target.type == "dir":
                fs.mkdir(abs_path)
            else:
                return RD.failed(f"Cannot make {target.type} path")
            return RD.success(TreeNode.info(abs_path, reroot=self.user_dir))
        except Exception as e:
            return RD.failed(f"{e.__class__}: {e}")

    def move(self, target: Target):
        try:
            old_path = self.get_and_check(target.source)
            new_path = fs.abspath(f"{self.user_dir}/{target.dest}")
            fs.move(old_path, new_path)
            return RD.success(TreeNode.info(new_path, reroot=self.user_dir))
        except FileNotFoundError:
            return RD.failed(f"Source path not found: {target.source}")

    def copy(self, target: Target):
        try:
            old_path = self.get_and_check(target.source)
            new_path = fs.abspath(f"{self.user_dir}/{target.dest}")
            if fs.isdir(old_path):
                fs.copy_dir(old_path, new_path)
            else:
                fs.copy_file(old_path, new_path)
            return RD.success(TreeNode.info(new_path, reroot=self.user_dir))
        except FileNotFoundError:
            return RD.failed(f"Path not found: {target.source}")
        except Exception as e:
            return RD.failed(e)

    def remove(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    def create(self, *args, **kwargs):
        return self.make(*args, **kwargs)
