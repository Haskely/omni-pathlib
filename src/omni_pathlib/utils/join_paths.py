import os.path
from omni_pathlib.utils.is_absolute_path import is_absolute_path


def join_paths(base: str, other: str) -> str:
    """连接两个路径

    Args:
        base: 基础路径
        other: 要连接的路径

    Returns:
        str: 规范化后的完整路径
    """
    # 如果 other 是绝对路径，直接返回
    if is_absolute_path(other):
        return other

    # 获取协议前缀（如果有的话）
    protocol = ""
    if "://" in base:
        protocol = base[: base.index("://") + 3]
        base = base[base.index("://") + 3 :]

    # 使用 os.path.normpath 规范化路径
    joined = os.path.normpath(os.path.join(base.rstrip("/"), other.lstrip("/")))

    # 如果有协议前缀，添加回去
    if protocol:
        joined = protocol + joined

    return joined


if __name__ == "__main__":
    for base, other in [
        ("/a/b/c", "d/e/f"),
        ("a/b/c", "d/e/f"),
        ("http://a/b/c", "d/e/f"),
        ("file://a/b/c", "d/e/f"),
        ("C:/a/b/c", "d/e/f"),
        ("http://a/b/c", "/d/e/f"),
        ("file://a/b/c", "/d/e/f"),
        ("C:/a/b/c", "/d/e/f"),
        ("http://a/b/c/", "d/e/f"),
        ("file://a/b/c/", "d/e/f"),
        ("C:/a/b/c/", "d/e/f"),
    ]:
        print(f"{base} / {other} = {join_paths(base, other)}")
