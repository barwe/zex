def as_variable_name(s: str):
    """将字符串转换为Python的合法变量名称"""
    import re, keyword

    # 移除非法字符并替换为下划线
    valid_string = re.sub(r"\W+", "_", s)

    # 如果字符串以数字开头，则在开头添加下划线
    if valid_string[0].isdigit():
        valid_string = "_" + valid_string

    # 如果字符串是Python的关键字，则在末尾添加下划线
    if keyword.iskeyword(valid_string):
        valid_string += "_"

    return valid_string


def hash16(text: str):
    import hashlib

    # 使用SHA256哈希算法
    hash_object = hashlib.sha256(text.encode("utf-8"))
    # 获取哈希值的十六进制表示
    hash_hex = hash_object.hexdigest()
    # 截取前16个字符，并转换为大写
    result = hash_hex[:16].upper()
    return result


def rstr(size: int):
    import random, string

    letters = string.ascii_letters
    return "".join(random.sample(letters, size))


def is_valid_variable_name(variable_name: str):
    import keyword

    if keyword.iskeyword(variable_name):
        return False
    if variable_name.isidentifier():
        return True
    return False


def maybe_int(v):
    try:
        return int(v)
    except Exception:
        return None
