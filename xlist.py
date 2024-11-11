from typing import Sequence, Callable, Union, List
from .types import T


def get(arr: Sequence[T], match: Callable[[T], bool]):
    for item in arr:
        if match(item):
            return item
    return None


def index(arr: Sequence[T], match: Callable[[T], bool]):
    for index, item in enumerate(arr):
        if match(item):
            return index
    return -1


def pick(arr: Sequence[T], match: Callable[[T], bool]) -> List[T]:
    new_arr = []
    for item in arr:
        if match(item):
            new_arr.append(item)
    return new_arr


def omit(arr: Sequence[T], match: Callable[[T], bool]) -> List[T]:
    new_arr = []
    for item in arr:
        if not match(item):
            new_arr.append(item)
    return new_arr


def unique(arr: Sequence[T]) -> List[T]:
    s = set()
    a = []
    for i in arr:
        if i not in s:
            a.append(i)
            s.add(i)
    return a


def diff(target, ref, key):
    """比较两个数组。Returns `(created, removed, other_target, other_ref)`"""
    created, removed, other_t, other_r = [], [], [], []
    tks = [key(d) for d in target]
    rks = [key(d) for d in ref]
    tqd = {k: d for k, d in zip(tks, target)}
    rqd = {k: d for k, d in zip(rks, ref)}
    for k in tks:
        if k not in rqd:
            created.append(tqd[k])
        else:
            other_t.append(tqd[k])
    for k in rks:
        if k not in tqd:
            removed.append(rqd[k])
        else:
            other_r.append(rqd[k])
    return created, removed, other_t, other_r


def expand_id_list(arr: Sequence[Union[int, str]], sep="-"):
    rd = []
    for i in arr:
        if isinstance(i, int):
            rd.append(i)
        elif isinstance(i, str):
            x = i.replace(" ", "")
            if sep in x:
                start, end = x.split(sep)
                for j in range(int(start), int(end) + 1):
                    rd.append(j)
            else:
                rd.append(int(x))
    return rd


def update(target: List[T], source: Sequence[T], key=None, merge=None):
    """
    使用一个列表更新另一个列表.
    - `target`: 待更新的列表
    - `source`: 提供更新数据的列表
    - `key`: 判断两个列表元素是否相等的函数, 默认为 `lambda x: x`, 一般应该返回一个字符串
    - `merge`: 合并两个列表元素的函数, 默认为 `lambda t, s: s`, t 表示 target 中的元素, s 表示 source 中的元素, 返回合并后的结果
    """
    if key is None:
        key = lambda x: x
    if merge is None:
        merge = lambda t, s: s

    ta = list(range(len(target)))
    tk_dict = {i: key(target[i]) for i in ta}

    for item in source:
        s_k = key(item)
        for i in ta:
            t_k = tk_dict[i]
            if t_k == s_k:
                target[i] = merge(target[i], item)
                break
        else:
            target.append(item)

    return target
