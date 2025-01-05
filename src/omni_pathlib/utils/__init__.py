
def is_absolute_path(path: str) -> bool:
    """判断给定的路径字符串是否为绝对路径"""
    return path.startswith(('//', '/', 'http://', 'https://', 's3://', 'file://'))


def guess_protocol(path: str) -> str:
    """从路径中提取协议"""
    if path.startswith(('http://', 'https://')):
        return 'http'
    elif path.startswith('s3://'):
        return 's3'
    elif path.startswith('file://') or path.startswith('/'):
        return 'file'
    return 'file'  # 默认为文件协议


def join_paths(base: str, other: str) -> str:
    """连接两个路径"""
    return f"{base.rstrip('/')}/{other.lstrip('/')}"