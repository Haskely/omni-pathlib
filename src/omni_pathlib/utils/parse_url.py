from dataclasses import dataclass


@dataclass
class PathInfo:
    url: str
    scheme: str
    schema_parts: list[str]
    path: str
    name: str
    stem: str
    suffix: str
    parent: str
    parts: list[str]


def parse_url(url: str) -> PathInfo:
    # 处理空URL
    if not url:
        return PathInfo(url, "", [], "", "", "", "", "", [])

    # 解析scheme
    scheme = ""
    schema_parts = []
    path = url
    if "://" in url:
        scheme, path = url.split("://", 1)
        schema_parts = scheme.split("+")

    # 解析路径组件
    path = path.rstrip("/")  # 移除末尾的斜杠
    parts = path.split("/")
    name = parts[-1] if parts else ""

    # 解析文件名组件
    stem = name
    suffix = ""
    if name and "." in name:
        stem, suffix = name.rsplit(".", 1)
        suffix = "." + suffix

    # 构建父路径
    parent = "/".join(parts[:-1]) if len(parts) > 1 else ""
    if scheme:
        parent = f"{scheme}://{parent}"

    return PathInfo(
        url=url,
        scheme=scheme,
        schema_parts=schema_parts,
        path=path,
        name=name,
        stem=stem,
        suffix=suffix,
        parent=parent,
        parts=parts,
    )


if __name__ == "__main__":
    from rich import print
    from rich.table import Table

    table = Table(title="Path Protocol")
    table.add_column("Path")
    table.add_column("Protocol")

    for path in [
        "",
        ".",
        "..",
        "./",
        "../",
        "/",
        "//",
        "///",
        "~",
        "~/",
        "s3://",
        "s3://bucket",
        "s3://bucket/",
        "s3://bucket/path",
        "s3://bucket/path/",
        "s3://bucket/path/to/file.txt",
        "s3+profile://bucket/path/to/file.txt",
        "http://bucket/path/to/file.txt",
        "https://bucket/path/to/file.txt",
        "file://bucket/path/to/file.txt",
        "/bucket/path/to/file.txt",
        "bucket/path/to/file.txt",
        "./bucket/path/to/file.txt",
        "../bucket/path/to/file.txt",
        "~/bucket/path/to/file.txt",
        "git://bucket/path/to/file.txt",
        "ftp://bucket/path/to/file.txt",
        "sftp://bucket/path/to/file.txt",
        "ssh://bucket/path/to/file.txt",
        "scp://bucket/path/to/file.txt",
        "s3+test_profile://bucket/path/to/file.txt",
    ]:
        table.add_row(path, str(parse_url(path)))

    print(table)
