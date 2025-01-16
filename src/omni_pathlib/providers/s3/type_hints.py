from typing_extensions import TypedDict, NotRequired


class S3ListObjectsContent(TypedDict):
    Key: str
    LastModified: str
    ETag: str
    Size: int
    StorageClass: str


class S3ListObjectsCommonPrefixes(TypedDict):
    Prefix: str


class S3ListObjectsResponse(TypedDict):
    Name: str
    Prefix: str | None
    KeyCount: int
    MaxKeys: int
    IsTruncated: bool
    Contents: list[S3ListObjectsContent]
    CommonPrefixes: list[S3ListObjectsCommonPrefixes]
    NextContinuationToken: NotRequired[str]


class S3ObjectMetadata(TypedDict):
    ContentLength: int
    ContentType: str | None
    ETag: str | None
    LastModified: str | None


class S3DeleteResult(TypedDict):
    Deleted: list[str]
    Error: list[dict[str, str | None]]
