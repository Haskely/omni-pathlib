from curl_cffi import requests
from typing import Iterator
import xmltodict
from omni_pathlib.providers.s3.sign_request import sign_request
from omni_pathlib.providers.s3.type_hints import (
    S3DeleteResult,
    S3ListObjectsResponse,
)
from omni_pathlib.utils.raise_for_status_with_text import (
    curl_cffi_raise_for_status_with_text,
)
from urllib.parse import urljoin


DEFAULT_IS_SIGN_PAYLOAD = False


def upload_file(
    bucket: str,
    key: str,
    data: bytes,
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    is_sign_payload: bool = DEFAULT_IS_SIGN_PAYLOAD,
) -> bool:
    """
    上传文件到 S3

    Args:
        bucket: 存储桶名称
        key: 对象键名
        data: 要上传的字节数据
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        is_sign_payload: 是否使用签名的 payload

    Returns:
        bool: 上传是否成功
    """
    uri = f"/{bucket}/{key}"
    host = endpoint.replace("https://", "").replace("http://", "")

    signed_headers = sign_request(
        method="PUT",
        host=host,
        region=region,
        access_key=access_key,
        secret_key=secret_key,
        uri=uri,
        payload=data if is_sign_payload else None,
    )

    response = requests.put(
        urljoin(endpoint, signed_headers["signed_url"]),
        data=data,
        headers=signed_headers["headers"],
    )
    curl_cffi_raise_for_status_with_text(response)
    return True


def download_file(
    bucket: str,
    key: str,
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    is_sign_payload: bool = DEFAULT_IS_SIGN_PAYLOAD,
) -> bytes:
    """
    从 S3 下载文件

    Args:
        bucket: 存储桶名称
        key: 对象键名
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        is_sign_payload: 是否使用签名的 payload

    Returns:
        bytes: 下载的文件内容
    """
    uri = f"/{bucket}/{key}"
    host = endpoint.replace("https://", "").replace("http://", "")

    signed_headers = sign_request(
        method="GET",
        host=host,
        region=region,
        access_key=access_key,
        secret_key=secret_key,
        uri=uri,
        payload=b"" if is_sign_payload else None,
    )

    response = requests.get(
        urljoin(endpoint, signed_headers["signed_url"]),
        headers=signed_headers["headers"],
    )
    curl_cffi_raise_for_status_with_text(response)
    return response.content


def list_objects(
    bucket: str,
    prefix: str,
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    delimiter: str | None = None,
    continuation_token: str | None = None,
    max_keys: int = 1000,
    is_sign_payload: bool = DEFAULT_IS_SIGN_PAYLOAD,
) -> S3ListObjectsResponse:
    """
    列出 S3 存储桶中的对象

    Args:
        bucket: 存储桶名称
        prefix: 共同前缀
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        delimiter: 用于分组结果的分隔符
        continuation_token: 分页标记
        max_keys: 单次返回的最大对象数量
        is_sign_payload: 是否使用签名的 payload

    Returns:
        dict: ListObjectsV2 响应数据
    """
    uri = f"/{bucket}"
    host = endpoint.replace("https://", "").replace("http://", "")

    query_params = {"list-type": "2", "max-keys": str(max_keys)}

    if prefix:
        query_params["prefix"] = prefix
    if continuation_token:
        query_params["continuation-token"] = continuation_token
    if delimiter:
        query_params["delimiter"] = delimiter

    signed_result = sign_request(
        method="GET",
        host=host,
        region=region,
        access_key=access_key,
        secret_key=secret_key,
        uri=uri,
        query_params=query_params,
        payload=b"" if is_sign_payload else None,
    )

    response = requests.get(
        urljoin(endpoint, signed_result["signed_url"]), headers=signed_result["headers"]
    )
    curl_cffi_raise_for_status_with_text(response)
    _result = xmltodict.parse(response.text)
    assert len(_result) == 1, f"response should be a single dict, but got {_result}"
    _result = _result[next(iter(_result))]
    result: S3ListObjectsResponse = _result | {
        "KeyCount": int(_result.get("KeyCount")),
        "MaxKeys": int(_result.get("MaxKeys")),
        "IsTruncated": _result.get("IsTruncated") == "true",
    }
    if "Contents" in result and not isinstance(result["Contents"], list):
        result["Contents"] = [result["Contents"]]
    if "CommonPrefixes" in result and not isinstance(result["CommonPrefixes"], list):
        result["CommonPrefixes"] = [result["CommonPrefixes"]]

    return result


def list_objects_iter(
    bucket: str,
    prefix: str,
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    delimiter: str | None = None,
    continuation_token: str | None = None,
    max_keys: int = 1000,
    is_sign_payload: bool = DEFAULT_IS_SIGN_PAYLOAD,
) -> Iterator[S3ListObjectsResponse]:
    """
    列出 S3 存储桶中的对象的迭代器版本

    Args:
        bucket: 存储桶名称
        prefix: 共同前缀
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        delimiter: 用于分组结果的分隔符
        continuation_token: 分页标记
        max_keys: 单次返回的最大对象数量
        is_sign_payload: 是否使用签名的 payload

    Returns:
        Iterator[dict]: 包含对象信息的字典
    """
    while True:
        response = list_objects(
            bucket=bucket,
            endpoint=endpoint,
            region=region,
            access_key=access_key,
            secret_key=secret_key,
            prefix=prefix,
            delimiter=delimiter,
            continuation_token=continuation_token,
            max_keys=max_keys,
            is_sign_payload=is_sign_payload,
        )

        yield response

        if not response.get("IsTruncated"):
            break

        continuation_token = response.get("NextContinuationToken")


def listdir_iter(
    bucket: str,
    key: str,
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    max_keys: int = 1000,
    is_sign_payload: bool = True,
) -> Iterator[S3ListObjectsResponse]:
    """
    列出指定路径下的文件和文件夹的迭代器版本

    Args:
        bucket: 存储桶名称
        key: 要列出内容的路径（文件夹）
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        max_keys: 每次请求的最大对象数量
        is_sign_payload: 是否使用签名的 payload

    Yields:
        tuple[list[str], list[str]]: (文件夹列表, 文件列表) 的批次数据
    """
    if key and not key.endswith("/"):
        key += "/"

    yield from list_objects_iter(
        bucket=bucket,
        prefix=key,
        endpoint=endpoint,
        region=region,
        access_key=access_key,
        secret_key=secret_key,
        delimiter="/",
        max_keys=max_keys,
        is_sign_payload=is_sign_payload,
    )


def head_object(
    bucket: str,
    key: str,
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    is_sign_payload: bool = DEFAULT_IS_SIGN_PAYLOAD,
) -> dict:
    """
    检查 S3 对象是否存在并获取其元数据

    Args:
        bucket: 存储桶名称
        key: 对象键名
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        is_sign_payload: 是否使用签名的 payload

    Returns:
        dict: 包含对象元数据的字典，如果对象不存在则抛出异常
    """
    uri = f"/{bucket}/{key}"
    host = endpoint.replace("https://", "").replace("http://", "")

    signed_headers = sign_request(
        method="HEAD",
        host=host,
        region=region,
        access_key=access_key,
        secret_key=secret_key,
        uri=uri,
        payload=b"" if is_sign_payload else None,
    )

    response = requests.head(
        urljoin(endpoint, signed_headers["signed_url"]),
        headers=signed_headers["headers"],
    )
    curl_cffi_raise_for_status_with_text(response)

    return {
        "ContentLength": int(response.headers.get("Content-Length", 0)),
        "ContentType": response.headers.get("Content-Type"),
        "ETag": response.headers.get("ETag"),
        "LastModified": response.headers.get("Last-Modified"),
    }


def delete_object(
    bucket: str,
    key: str,
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    is_sign_payload: bool = DEFAULT_IS_SIGN_PAYLOAD,
) -> bool:
    """
    从 S3 删除文件

    Args:
        bucket: 存储桶名称
        key: 对象键名
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        is_sign_payload: 是否使用签名的 payload

    Returns:
        bool: 删除是否成功
    """
    uri = f"/{bucket}/{key}"
    host = endpoint.replace("https://", "").replace("http://", "")

    signed_headers = sign_request(
        method="DELETE",
        host=host,
        region=region,
        access_key=access_key,
        secret_key=secret_key,
        uri=uri,
        payload=b"" if is_sign_payload else None,
    )

    response = requests.delete(
        urljoin(endpoint, signed_headers["signed_url"]),
        headers=signed_headers["headers"],
    )
    curl_cffi_raise_for_status_with_text(response)
    return response.status_code == 204


def delete_objects(
    bucket: str,
    keys: list[str],
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    is_sign_payload: bool = DEFAULT_IS_SIGN_PAYLOAD,
) -> S3DeleteResult:
    """
    批量删除 S3 对象

    Args:
        bucket: 存储桶名称
        keys: 对象键名列表
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        is_sign_payload: 是否使用签名的 payload

    Returns:
        dict: 删除结果
    """
    uri = f"/{bucket}"
    host = endpoint.replace("https://", "").replace("http://", "")

    objects_xml = "".join([f"<Object><Key>{key}</Key></Object>" for key in keys])
    payload = f'<?xml version="1.0" encoding="UTF-8"?><Delete><Quiet>false</Quiet>{objects_xml}</Delete>'.encode()

    query_params = {"delete": ""}

    signed_result = sign_request(
        method="POST",
        host=host,
        region=region,
        access_key=access_key,
        secret_key=secret_key,
        uri=uri,
        query_params=query_params,
        payload=payload if is_sign_payload else None,
    )

    response = requests.post(
        urljoin(endpoint, signed_result["signed_url"]),
        data=payload,
        headers=signed_result["headers"],
    )
    curl_cffi_raise_for_status_with_text(response)

    _result = xmltodict.parse(response.text)
    assert len(_result) == 1, f"response should be a single dict, but got {_result}"
    result: S3DeleteResult = _result[next(iter(_result))]
    if "Deleted" in result and not isinstance(result["Deleted"], list):
        result["Deleted"] = [result["Deleted"]]
    if "Error" in result and not isinstance(result["Error"], list):
        result["Error"] = [result["Error"]]

    return result


def create_bucket(
    bucket: str,
    endpoint: str,
    region: str,
    access_key: str,
    secret_key: str,
    is_sign_payload: bool = DEFAULT_IS_SIGN_PAYLOAD,
):
    """
    创建 S3 存储桶

    Args:
        bucket: 存储桶名称
        endpoint: S3 endpoint
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        is_sign_payload: 是否使用签名的 payload

    Returns:
        bool: 创建是否成功
    """
    uri = f"/{bucket}"
    host = endpoint.replace("https://", "").replace("http://", "")

    # 准备创建存储桶的 XML 配置
    if not region:
        location_constraint = b""
    else:
        location_constraint = f"""<?xml version="1.0" encoding="UTF-8"?>
            <CreateBucketConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
                <LocationConstraint>{region}</LocationConstraint>
            </CreateBucketConfiguration>""".encode()

    signed_headers = sign_request(
        method="PUT",
        host=host,
        region=region,
        access_key=access_key,
        secret_key=secret_key,
        uri=uri,
        payload=location_constraint if is_sign_payload else None,
    )

    response = requests.put(
        urljoin(endpoint, signed_headers["signed_url"]),
        data=location_constraint,
        headers=signed_headers["headers"],
    )
    curl_cffi_raise_for_status_with_text(response)
    if "Error" in response.text:
        raise ValueError(f"create bucket failed: {response.text}")
    return response.text


if __name__ == "__main__":
    from rich import print
    import json
    from moto.server import ThreadedMotoServer

    server = ThreadedMotoServer(port=0)
    server.start()
    host, port = server.get_host_and_port()
    print(f"started: http://{host}:{port}")
    if host == "0.0.0.0":
        host = "localhost"

    credentials = {
        "endpoint_url": f"http://{host}:{port}",
        "region_name": "unknown",
        "aws_access_key_id": "test",
        "aws_secret_access_key": "test",
    }

    print(f"Using profile: {credentials}")

    ak = credentials["aws_access_key_id"]
    sk = credentials["aws_secret_access_key"]
    endpoint = credentials["endpoint_url"]
    region = credentials.get("region", "unknown")
    bucket = "haskely"

    # 定义测试路径和文件
    TEST_PREFIX = "test_folder/"
    TEST_FILES = {
        f"{TEST_PREFIX}file1.txt": b"content of file1",
        f"{TEST_PREFIX}file2.txt": b"content of file2",
        f"{TEST_PREFIX}subfolder/file3.txt": b"content of file3",
        f"{TEST_PREFIX}subfolder/file4.txt": b"content of file4",
    }

    def setup_test_env():
        """创建测试环境"""
        print("正在创建测试环境...")

        create_bucket(bucket, endpoint, region, ak, sk)
        for key, content in TEST_FILES.items():
            upload_file(bucket, key, content, endpoint, region, ak, sk)
            print(f"已上传: {key}")

    def cleanup_test_env():
        """清理测试环境"""
        print("\n正在清理测试环境...")
        keys_to_delete = list(TEST_FILES.keys())
        result = delete_objects(bucket, keys_to_delete, endpoint, region, ak, sk)
        print(f"清理结果: {result}")
        server.stop()

    def test_listdir():
        """测试列出文件夹内容"""
        print("\n测试列出文件夹内容:")
        print(f"列出 {TEST_PREFIX} 的内容:")
        for response in listdir_iter(bucket, TEST_PREFIX, endpoint, region, ak, sk):
            print(f"找到的内容: {json.dumps(response, indent=4)}")

        print(f"\n列出 {TEST_PREFIX}subfolder/ 的内容:")
        for response in listdir_iter(
            bucket, f"{TEST_PREFIX}subfolder/", endpoint, region, ak, sk
        ):
            print(f"找到的内容: {json.dumps(response, indent=4)}")

    def test_head_and_download():
        """测试文件元数据和下载"""
        print("\n测试文件元数据和下载:")
        test_key = f"{TEST_PREFIX}file1.txt"

        # 测试 head_object
        metadata = head_object(bucket, test_key, endpoint, region, ak, sk)
        print(f"文件元数据: {metadata}")

        # 测试下载
        content = download_file(bucket, test_key, endpoint, region, ak, sk)
        print(f"下载的内容: {content.decode()}")

    def test_delete_operations():
        """测试删除操作及验证"""
        print("\n测试删除操作:")
        test_key = f"{TEST_PREFIX}file2.txt"

        # 删除前先验证文件存在
        try:
            metadata = head_object(bucket, test_key, endpoint, region, ak, sk)
            print(f"删除前文件存在，元数据: {metadata}")
        except Exception as e:
            print(f"文件不存在: {e}")
            return

        # 测试单个文件删除
        success = delete_object(bucket, test_key, endpoint, region, ak, sk)
        print(f"删除文件 {test_key} {'成功' if success else '失败'}")

        # 验证文件已被删除
        try:
            head_object(bucket, test_key, endpoint, region, ak, sk)
            print("错误：文件仍然存在！")
        except Exception as e:
            print(f"验证成功：文件已被删除 ({str(e)})")

    def run_all_tests():
        """运行所有测试"""
        try:
            setup_test_env()
            test_listdir()
            test_head_and_download()
            test_delete_operations()
        finally:
            cleanup_test_env()

    run_all_tests()
