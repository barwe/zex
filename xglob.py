import re
from typing import Sequence
from .decorators import cache


def expand_braces(pattern: str):
    """
    将模式字符串中格式为 `{xxx,yyy}` 的子串替换成 `(xxx|yyy)`
    """

    # 定义一个递归函数来展开括号内的内容: {a,b} => (a|b)
    def replace_braces(match: re.Match):
        content: str = match.group(1)
        body = "|".join(map(re.escape, content.split(",")))
        return f"({body})"

    # 使用正则表达式查找 {xxx,yyy} 模式并替换
    brace_pattern = re.compile(r"\{([^{}]*)\}")
    while brace_pattern.search(pattern):
        pattern = brace_pattern.sub(replace_braces, pattern)

    return pattern


@cache()
def translate_hashtags(pattern: str):
    pattern = pattern.replace(r"##", r".*?")
    pattern = pattern.replace(r"#", r"[^/]+")
    return pattern


def path_matches_pattern(path: str, pattern: str):
    # pattern = re.escape(pattern)
    # pattern = expand_braces(pattern)
    pattern = translate_hashtags(pattern)
    regex = re.compile(pattern)
    return bool(regex.fullmatch(path))


def path_matches_any_patterns(path: str, patterns: Sequence[str]):
    return any((path_matches_pattern(path, pattern) for pattern in patterns))


if __name__ == "__main__":
    path_pattern = r"##(b|c)/d/(e|f|g).txt"
    test_paths = [
        "/a/b/d/e.txt",
        "/a/b/d/f.txt",
        "/a/b/d/g.txt",
        "/a/c/d/e.txt",
        "/a/c/d/f.txt",
        "/a/0/d/g.txt",
        "/a/b/d/h.txt",
        "/a/c/d/h.txt",
    ]
    for test_path in test_paths:
        print("[DEBUG]", test_path, path_matches_pattern(test_path, path_pattern))
