import os.path
from urllib.parse import urlparse


def is_absolute_path(path: str) -> bool:
    """判断给定的路径字符串是否为绝对路径"""
    return path.startswith(("//", "/", "http://", "https://", "s3://", "file://"))


def guess_protocol(path: str) -> str | None:
    """从路径中提取协议"""
    if path.startswith(("http://", "https://")):
        return "http"
    elif path.startswith("s3://"):
        return "s3"
    elif path.startswith("file://") or path[0] in (".", "/", "\\", "~"):
        return "file"
    else:
        url = urlparse(path)
        if url.scheme:
            return url.scheme
        else:
            return None


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
    for prefix in ("file://", "http://", "https://", "s3://"):
        if base.startswith(prefix):
            protocol = prefix
            base = base[len(prefix) :]
            break

    # 使用 os.path.normpath 规范化路径
    joined = os.path.normpath(os.path.join(base.rstrip("/"), other.lstrip("/")))

    # 如果有协议前缀，添加回去
    if protocol:
        joined = protocol + joined

    return joined
