from .types import RoRecord, Record
from typing import Sequence, Union


def split_to_keys(x: Union[str, Sequence[str]]):
    if isinstance(x, str):
        return x.split(" ")
    return x


class LIST_POLICY:
    OVERRIDE = 0  #
    ERROR = 1


def isdict(v):
    return isinstance(v, dict)


def pick_by(data, func):
    return {k: v for k, v in data.items() if func(k, v)}


def pick_keys(dct: RoRecord, keys, allow_none=False):
    new_dct: Record = {}
    for k in split_to_keys(keys):
        if k in dct:
            new_dct[k] = dct[k]
        elif allow_none:
            new_dct[k] = None
    return new_dct


def pick_keys_with_defaults(dct, keys, defaults):
    data = pick_keys(dct, keys)
    for k in defaults:
        if k not in data:
            data[k] = defaults[k]
    return data


def pick_attrs(obj, keys, allow_none=False):
    new_dct: Record = {}
    for k in split_to_keys(keys):
        if hasattr(obj, k):
            new_dct[k] = getattr(obj, k)
        elif allow_none:
            new_dct[k] = None
    return new_dct


def omit_keys(dct: RoRecord, keys):
    new_dct: Record = {}
    kset = split_to_keys(keys)
    for k in dct.keys():
        if k not in kset:
            new_dct[k] = dct[k]
    return new_dct


def pop_keys(dct: Record, keys):
    return {k: dct.pop(k) for k in split_to_keys(keys) if k in dct}


def assign(target: Record, source: RoRecord, overwrite=True):
    for k in source.keys():
        if k in target:
            if overwrite:
                target[k] = source[k]
        else:
            target[k] = source[k]
    return target


LIST_POLICY = LIST_POLICY


def update_incremental(
    target: Record,
    source: RoRecord,
    list_policy=LIST_POLICY.ERROR,
    check_base_types=False,  # 是否检查简单数据类型的类型
):
    """增量更新字典。具体的更新策略如下：
    - 对于基本的数据类型，如布尔值、数值和字符串，直接覆盖原有值
    - 对于字典，递归调用本函数更新
    - 对于列表，由 lsit_policy 参数决定更新策略
    """
    for k in source.keys():
        if k not in target:
            target[k] = source[k]
            continue

        tv = target[k]
        sv = source[k]
        if sv == tv:
            continue

        if sv == None:
            target[k] = None

        # 支持新值与旧值类型匹配
        elif isinstance(sv, (bool, int, float, str)):
            if check_base_types:
                assert type(tv) == type(sv), f"{k}: 新值类型与旧值不一致 {type(sv)} != {type(tv)}"
            target[k] = sv

        # 新值是列表时,支持设置更新策略; 旧值必须也是列表
        elif isinstance(sv, list):
            assert isinstance(tv, list), f"{k}: 新值是列表时旧值也必须是列表"
            if list_policy == LIST_POLICY.ERROR:
                raise Exception("Cannot update `list` element incrementally.")
            elif list_policy == LIST_POLICY.OVERRIDE:
                target[k] = sv
            else:
                raise ValueError(f"Invalid list policy: {list_policy}")

        # 新值是字典时,旧值也必须是字典
        elif isinstance(sv, dict):
            assert isinstance(tv, dict), f"{k}: 新值是字典时旧值也必须是字典"
            target[k] = update_incremental(
                target[k],
                sv,
                list_policy=list_policy,
                check_base_types=check_base_types,
            )

        # 新值是其他数据类型
        else:
            raise Exception(f"Unsupported data type: {type(tv)}")

    return target


def diff(target, ref):
    nd = {}
    od = {}
    for k in target:
        if k in ref:
            if isinstance(target[k], dict):
                nd[k], od[k] = diff(target[k], ref[k])
            elif target[k] != ref[k]:
                nd[k] = target[k]
                od[k] = ref[k]
        else:
            od[k] = target[k]
    for k in ref:
        if k not in target:
            nd[k] = ref[k]
    return nd, od


def get2(data, keys, raise_=True, default=None):
    for k in split_to_keys(keys):
        if k in data:
            return data[k]
    if raise_:
        raise KeyError(f"{keys} not in data")
    return default
