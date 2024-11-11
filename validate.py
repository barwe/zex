from typing import Mapping, Iterable, Any

RoRecord = Mapping[str, Any]
NO_DEFAULT = "__NO_DEFAULT_VALUE_PROVIDED_FOR_THIS_KEY__"


class ValidateDataError(Exception):
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(*args)


def _is_in_dtypes(cls, dtype_or_dtypes):
    if isinstance(dtype_or_dtypes, Iterable):
        return cls in dtype_or_dtypes
    return cls == dtype_or_dtypes


def validate_data(data: dict, rules: Mapping[str, Any]):
    """
    字典验证，成功返回None，失败返回错误消息。
    ```ts
    interface Rules {
        [key: string]: {
            // 该字段是否是必须的
            required?: boolean
            // 该字段值的数据类型
            dtype?: <type_function>
            // 如果字段值是一个数组，其列表项的数据类型
            item_dtype?: <type_function>
            // 如果字段值是一个数组且列表项为字典，对其进行递归验证
            item_rules?: Rules
            // 默认值
            default?: any
        }
    }
    ```
    """
    for k, c in rules.items():
        # 必要性验证
        if c.get("required", False) and k not in data:
            return f"字典缺少必要的键 {k}"

        if k not in data and c.get("default", NO_DEFAULT) != NO_DEFAULT:
            data[k] = c["default"]

        if k in data:
            v = data.get(k)
            # 数据类型验证，键不存在时跳过
            dtype = c.get("dtype", None)
            if dtype and not isinstance(v, dtype):
                a = str(dtype)[8:-2]
                b = str(type(v))[8:-2]
                return f"{k} 值 ({v}) 的数据只能是 {a} 但实际上是 {b}"
            # 数据是列表时……
            if _is_in_dtypes(list, dtype):
                # 验证列表项数据类型
                item_dtype = c.get("item_dtype")
                if item_dtype:
                    for vi, vv in enumerate(v):
                        if not isinstance(vv, item_dtype):
                            a = str(item_dtype)[8:-2]
                            b = str(type(vv))[8:-2]
                            return f"{k} 列表的第 {vi+1} 项的数据类型只能是 {a} 但实际上是 {b}"
                # 列表项是字典时递归验证
                if _is_in_dtypes(dict, dtype):
                    item_rules = c.get("item_rules")
                    if item_rules:
                        for vi, vv in enumerate(v):
                            if msg := validate_data(vv, item_rules):
                                return f"{k} 列表第 {vi+1} 项的 {msg}"

            # 数据是字典时……
            if _is_in_dtypes(dict, dtype):
                rules = c.get("rules")
                if rules and (msg := validate_data(v, rules)):
                    return f"{k} 字典的 {msg}"

            # 枚举值验证
            if (choices := c.get("choices", None)) and v not in choices:
                a = ", ".join([str(i) for i in choices])
                return f"{k} 值 ({v}) 不在 {a} 中"

        # 自定义验证
        validator = c.get("validator", None)
        if validator is not None:
            if msg := validator(data):
                return msg
    return None


def _check_field_dtype(value, dtype_or_tuple):
    if isinstance(dtype_or_tuple, tuple):
        dtypes = dtype_or_tuple
    else:
        dtypes = (dtype_or_tuple,)
    if not isinstance(value, dtypes):
        dtypes_str = " | ".join([str(dt)[8:-2] for dt in dtypes])
        value_type_str = str(type(value))[8:-2]
        raise ValidateDataError(f"值 {value} 应该是 {dtypes_str} 类型，但实际上是 {value_type_str} 类型")
    return dtypes


def validate_data_v2(rawdata: dict, rules: Mapping[str, RoRecord], packet_name="数据集"):
    """
    `rules` 是一个字典，为每个字段指定验证规则: `{ 字段名称: 验证规则 }`。

    一个验证规则由如下几部分组成：
    - `required?: bool`: rawdata 中必须提供该字段，字段值为 `None` 时不会触发异常
    - `dtype?: bool | int | str | list | dict | ...`: 检查字段值的数据类型，类型不匹配时引发异常。也可以是类型的元祖，此时只要有一个类型匹配即可
    - `default?`: 当 `required` 为 `False` 时设置字段的默认值。如果指定了 `dtype`，默认值的类型必须与 `dtype` 值一致
    - `item_dtype: bool | int | str | list | dict | ...`: 如果字段值是一个列表，检查其列表项的数据类型，类型不匹配时引发异常。需要 `dtype` 中包含 `list` 才会触发此检查
    - `item_rules: { 字段名称: 验证规则 }`: 如果字段值是一个字典，递归调用本方法验证数据。需要 `item_dtype` 中包含 `dict` 才会触发此检查

    `packet_name` 指定错误消息的数据主体。
    """
    if packet_name == None:
        packet_name = ""

    filtered_data = {}

    for field, rule in rules.items():
        undefined = False
        if field not in rawdata:
            if rule.get("required", False):
                raise ValidateDataError(f"{packet_name}字段 {field} 是必须字段")
            if "default" in rule:
                rawdata[field] = rule["default"]
            else:
                rawdata[field] = None
                undefined = True

        # 字段没有有意义的值时，不再检查其余规则
        if undefined:
            filtered_data[field] = None
            continue

        value = rawdata.get(field)

        # 数据类型验证
        if "dtype" in rule:
            # 字段值的数据类型是否匹配
            try:
                _check_field_dtype(value, rule["dtype"])
            except ValidateDataError as e:
                raise ValidateDataError(f"{packet_name}字段 {field} 的{e.message}")

        # 字段值为列表时每个列表项都必须是 item_dtype 指定的类型
        if isinstance(value, list) and "item_dtype" in rule:
            for idx, val in enumerate(value):
                # 验证列表项数据类型
                try:
                    _check_field_dtype(val, rule["item_dtype"])
                except ValidateDataError as e:
                    raise ValidateDataError(f"{packet_name}列表字段 {field} 第 {idx} 项的{e.message}")
                # 列表项是字典时递归验证
                if isinstance(val, dict) and "item_rules" in rule:
                    try:
                        validate_data_v2(val, rule["item_rules"], packet_name=None)
                    except ValidateDataError as e:
                        raise ValidateDataError(f"{packet_name}列表字段 {field} 第 {idx} 项的{e.message}")

        # 字段值是字典时递归验证
        if isinstance(value, dict) and "rules" in rule:
            try:
                validate_data_v2(value, rule["rules"], packet_name=None)
            except ValidateDataError as e:
                raise ValidateDataError(f"{packet_name}字典字段 {field} 的{e.message}")

        # 枚举值验证
        if "choices" in rule and value not in (vs := rule["choices"]):
            a = ", ".join([str(i) for i in vs])
            raise ValidateDataError(f"{packet_name}枚举字段 {field} 的值 {value} 不在限定的集合 ({a}) 中")

        # 自定义验证
        if "validator" in rule:
            try:
                if err := rule["validator"](rawdata):
                    raise ValidateDataError(err)
            except ValidateDataError as e:
                raise ValidateDataError(f"{packet_name}字段 {field} 自定义验证失败: {e.message}")
            except Exception as e:
                raise ValidateDataError(f"{packet_name}字段 {field} 自定义验证失败: {e.args}")

        filtered_data[field] = value

    return filtered_data
