from urllib.parse import urlparse

SCHEMAS_TO_PROTOCOL = {
    "http": "http",
    "https": "http",
    "s3": "s3",
    "file": "file",
    "": "file",
}


def guess_protocol(path: str) -> str | None:
    """从路径中提取协议"""
    parsed = urlparse(path)

    first_schema = parsed.scheme.split("+")[0]

    return SCHEMAS_TO_PROTOCOL.get(first_schema, first_schema)


if __name__ == "__main__":
    from rich import print
    from rich.table import Table

    table = Table(title="Path Protocol")
    table.add_column("Path")
    table.add_column("Protocol")

    for path in [
        "s3://bucket/path/to/file.txt",
        "s3+basemind://bucket/path/to/file.txt",
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
    ]:
        table.add_row(path, str(guess_protocol(path)))

    print(table)
