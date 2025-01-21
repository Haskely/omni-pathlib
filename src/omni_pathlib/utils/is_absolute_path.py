import os.path


def is_absolute_path(path: str) -> bool:
    """判断给定的路径字符串是否为绝对路径"""
    if "://" in path:
        return True
    return os.path.isabs(path)


if __name__ == "__main__":
    for path in [
        "/a/b/c",
        "a/b/c",
        "http://a/b/c",
        "s3://a/b/c",
        "file://a/b/c",
        "C:/a/b/c",
    ]:
        print(f"{path}: {is_absolute_path(path)}")
