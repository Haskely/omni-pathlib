import pytest
from moto.server import ThreadedMotoServer
from omni_pathlib.providers.s3 import S3Path
from unittest.mock import patch, MagicMock
from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import Response
import aiohttp
from typing import Dict, Generator


@pytest.fixture(scope="module")
def moto_server() -> Generator[str, None, None]:
    """创建 Moto 服务器实例"""
    server = ThreadedMotoServer(port=0)
    server.start()
    host, port = server.get_host_and_port()
    if host == "0.0.0.0":
        host = "localhost"
    yield f"http://{host}:{port}"
    server.stop()


@pytest.fixture(scope="function")
def test_bucket(moto_server: str) -> str:
    """创建测试用的 bucket"""
    bucket_name = "test-bucket"
    # 使用 S3Path 创建 bucket
    from omni_pathlib.providers.s3.sync_ops import create_bucket

    create_result = create_bucket(bucket_name, moto_server, "", "testing", "testing")
    print("DEBUG: create_result", create_result)

    return bucket_name


@pytest.fixture(scope="function")
def s3_config(moto_server: str) -> Dict[str, str]:
    """提供 S3 配置的 fixture"""
    return {
        "endpoint_url": moto_server,
        "region_name": "us-east-1",  # 设置默认 region
        "aws_access_key_id": "testing",
        "aws_secret_access_key": "testing",
    }


def test_s3_path_basic(test_bucket: str, s3_config: Dict[str, str]) -> None:
    """测试 S3Path 的基本功能"""
    path = S3Path(
        f"s3://{test_bucket}/test-测试.txt",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    path.write_text("测试内容")

    assert path.exists()
    assert path.read_text() == "测试内容"

    # 测试写入操作
    new_path = S3Path(
        f"s3://{test_bucket}/new-新文件.txt",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    new_path.write_text("新内容")
    assert new_path.exists()
    assert new_path.read_text() == "新内容"


@pytest.mark.asyncio
async def test_s3_path_async(test_bucket: str, s3_config: Dict[str, str]) -> None:
    """测试 S3Path 的异步功能"""
    path = S3Path(
        f"s3://{test_bucket}/async_test-异步测试.txt",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    await path.async_write_text("异步测试内容")

    assert await path.async_exists()
    assert await path.async_read_text() == "异步测试内容"

    # 测试异步写入
    new_path = S3Path(
        f"s3://{test_bucket}/async_new-异步新文件.txt",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    await new_path.async_write_text("异步新内容")
    assert await new_path.async_exists()
    assert await new_path.async_read_text() == "异步新内容"


def test_s3_path_iterdir(test_bucket: str, s3_config: Dict[str, str]) -> None:
    """测试目录遍历功能"""
    # 创建测试文件结构
    files = [
        "dir1/file1-文件1.txt",
        "dir1/file2-文件2.txt",
        "dir2/file3-文件3.txt",
        "file4-文件4.txt",
        "file5-文件5.txt",
    ]

    for file_path in files:
        path = S3Path(
            f"s3://{test_bucket}/{file_path}",
            endpoint_url=s3_config["endpoint_url"],
            region_name=s3_config["region_name"],
            aws_access_key_id=s3_config["aws_access_key_id"],
            aws_secret_access_key=s3_config["aws_secret_access_key"],
        )
        path.write_text("content")

    # 测试根目录遍历
    root = S3Path(
        f"s3://{test_bucket}",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    items = {str(item) for item in root.iterdir()}
    print("DEBUG: items", items)
    target_items = {
        "s3://test-bucket/dir1/",
        "s3://test-bucket/dir2/",
        "s3://test-bucket/file4-文件4.txt",
        "s3://test-bucket/file5-文件5.txt",
    }
    assert target_items.issubset(items), f"extra items: {target_items - items}"

    # 测试子目录遍历
    dir1 = S3Path(
        f"s3://{test_bucket}/dir1",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    items = {str(item) for item in dir1.iterdir()}
    print("DEBUG: items", items)
    # FIXME: 这里返回的 items 是空的
    target_items = {
        "s3://test-bucket/dir1/file1-文件1.txt",
        "s3://test-bucket/dir1/file2-文件2.txt",
    }
    assert target_items.issubset(items), f"extra items: {target_items - items}"


@pytest.mark.asyncio
async def test_s3_path_async_iterdir(
    test_bucket: str, s3_config: Dict[str, str]
) -> None:
    """测试异步目录遍历功能"""
    # 创建测试文件结构
    files = [
        "async_dir1/file1-文件1.txt",
        "async_dir1/file2-文件2.txt",
        "async_dir2/file3-文件3.txt",
    ]
    for file_path in files:
        path = S3Path(
            f"s3://{test_bucket}/{file_path}",
            endpoint_url=s3_config["endpoint_url"],
            region_name=s3_config["region_name"],
            aws_access_key_id=s3_config["aws_access_key_id"],
            aws_secret_access_key=s3_config["aws_secret_access_key"],
        )
        path.write_text("content")

    # 测试异步遍历
    root = S3Path(
        f"s3://{test_bucket}/",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    items = {str(item) async for item in root.async_iterdir()}
    print("DEBUG: items", items)
    target_items = {"s3://test-bucket/async_dir1/", "s3://test-bucket/async_dir2/"}
    assert target_items.issubset(items), f"extra items: {target_items - items}"


def test_s3_path_with_profile_in_scheme(
    test_bucket: str, s3_config: Dict[str, str]
) -> None:
    """测试通过 URL scheme 指定 profile 的功能"""
    # 设置测试用的凭证配置
    from omni_pathlib.providers.s3.credentials import CREDENTIALS

    CREDENTIALS["default"] = {}
    CREDENTIALS["test_profile"] = {
        "endpoint_url": s3_config["endpoint_url"],
        "region_name": s3_config["region_name"],
        "aws_access_key_id": s3_config["aws_access_key_id"],
        "aws_secret_access_key": s3_config["aws_secret_access_key"],
    }

    # 测试使用 scheme 中的 profile
    path = S3Path(f"s3+test_profile://{test_bucket}/profile_test.txt")
    path.write_text("通过 profile 写入的内容")

    assert path.exists()
    assert path.read_text() == "通过 profile 写入的内容"
    assert path.path_info.scheme == "s3+test_profile"
    assert path.profile_name == "test_profile"
    for item in path.parent.iterdir():
        assert item.path_info.scheme == "s3+test_profile"
        assert item.profile_name == "test_profile"

    # 测试 profile 优先级：参数优先于 URL scheme
    path_with_both = S3Path(
        f"s3+test_profile://{test_bucket}/priority_test.txt", profile_name="default"
    )
    assert path_with_both.profile_name == "default"

    # 测试无效的 profile
    with pytest.raises(
        ValueError,
        match="Profile Name from scheme.*not found in credentials, available profile names:.*",
    ):
        S3Path(f"s3+invalid_profile://{test_bucket}/error.txt")


@pytest.mark.asyncio
async def test_s3_path_with_profile_in_scheme_async(
    test_bucket: str, s3_config: Dict[str, str]
) -> None:
    """测试异步操作时通过 URL scheme 指定 profile 的功能"""
    # 设置测试用的凭证配置
    from omni_pathlib.providers.s3.credentials import CREDENTIALS

    CREDENTIALS["async_test_profile"] = {
        "endpoint_url": s3_config["endpoint_url"],
        "region_name": s3_config["region_name"],
        "aws_access_key_id": s3_config["aws_access_key_id"],
        "aws_secret_access_key": s3_config["aws_secret_access_key"],
    }

    # 测试异步操作
    path = S3Path(f"s3+async_test_profile://{test_bucket}/async_profile_test.txt")
    await path.async_write_text("异步通过 profile 写入的内容")

    assert await path.async_exists()
    assert await path.async_read_text() == "异步通过 profile 写入的内容"
    assert path.path_info.scheme == "s3+async_test_profile"
    assert path.profile_name == "async_test_profile"
    for item in path.parent.iterdir():
        assert item.path_info.scheme == "s3+async_test_profile"
        assert item.profile_name == "async_test_profile"


def test_s3_path_exists_404_handling(
    test_bucket: str, s3_config: Dict[str, str]
) -> None:
    """测试 S3Path.exists 方法处理 404 错误的情况"""
    path = S3Path(
        f"s3://{test_bucket}/non_existent_file.txt",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )

    # 确认不存在的文件返回 False
    assert not path.exists()

    # 模拟 HTTPError 异常，但 e.response 为 None 的情况
    mock_error = HTTPError("Not found", code=0, response=None)
    with patch(
        "omni_pathlib.providers.s3.sync_ops.head_object", side_effect=mock_error
    ):
        with pytest.raises(HTTPError):  # 应该引发异常，因为无法安全地访问 status_code
            path.exists()

    # 模拟 HTTPError 异常，e.response 不为 None 但 status_code 不是 404
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 403
    mock_error = HTTPError("Forbidden", code=0, response=mock_response)
    with patch(
        "omni_pathlib.providers.s3.sync_ops.head_object", side_effect=mock_error
    ):
        with pytest.raises(HTTPError):  # 应该引发异常，因为错误码不是 404
            path.exists()

    # 模拟 HTTPError 异常，e.response 不为 None 且 status_code 是 404
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 404
    mock_error = HTTPError("Not found", code=0, response=mock_response)
    with patch(
        "omni_pathlib.providers.s3.sync_ops.head_object", side_effect=mock_error
    ):
        assert not path.exists()  # 应该返回 False


@pytest.mark.asyncio
async def test_s3_path_async_exists_404_handling(
    test_bucket: str, s3_config: Dict[str, str]
) -> None:
    """测试 S3Path.async_exists 方法处理 404 错误的情况"""
    path = S3Path(
        f"s3://{test_bucket}/non_existent_file.txt",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )

    # 确认不存在的文件返回 False
    assert not await path.async_exists()

    # 模拟 ClientResponseError 异常，status 为 404
    mock_error = aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=404,
        message="Not found",
        headers=MagicMock(),
    )
    with patch(
        "omni_pathlib.providers.s3.async_ops.head_object", side_effect=mock_error
    ):
        assert not await path.async_exists()

    # 模拟 ClientResponseError 异常，status 不是 404
    mock_error = aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=403,
        message="Forbidden",
        headers=MagicMock(),
    )
    with patch(
        "omni_pathlib.providers.s3.async_ops.head_object", side_effect=mock_error
    ):
        with pytest.raises(
            aiohttp.ClientResponseError
        ):  # 应该引发异常，因为错误码不是 404
            await path.async_exists()


def test_s3_folder_exists(test_bucket: str, s3_config: Dict[str, str]) -> None:
    """测试 S3 文件夹的 exists 检测"""
    # 创建一些文件来形成文件夹结构
    files = [
        "folder1/file1.txt",
        "folder1/file2.txt",
        "folder1/subfolder/file3.txt",
        "folder2/file4.txt",
    ]

    for file_path in files:
        path = S3Path(
            f"s3://{test_bucket}/{file_path}",
            endpoint_url=s3_config["endpoint_url"],
            region_name=s3_config["region_name"],
            aws_access_key_id=s3_config["aws_access_key_id"],
            aws_secret_access_key=s3_config["aws_secret_access_key"],
        )
        path.write_text("content")

    # 测试文件夹存在（不带尾部斜杠）
    folder1 = S3Path(
        f"s3://{test_bucket}/folder1",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert folder1.exists(), "folder1 should exist"

    # 测试文件夹存在（带尾部斜杠）
    folder1_slash = S3Path(
        f"s3://{test_bucket}/folder1/",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert folder1_slash.exists(), "folder1/ should exist"

    # 测试子文件夹存在
    subfolder = S3Path(
        f"s3://{test_bucket}/folder1/subfolder",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert subfolder.exists(), "folder1/subfolder should exist"

    # 测试不存在的文件夹
    non_existent_folder = S3Path(
        f"s3://{test_bucket}/non_existent_folder",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert not non_existent_folder.exists(), "non_existent_folder should not exist"

    # 测试文件的 exists（确保文件检测仍然正常工作）
    file1 = S3Path(
        f"s3://{test_bucket}/folder1/file1.txt",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert file1.exists(), "folder1/file1.txt should exist"


@pytest.mark.asyncio
async def test_s3_folder_async_exists(
    test_bucket: str, s3_config: Dict[str, str]
) -> None:
    """测试 S3 文件夹的异步 exists 检测"""
    # 创建一些文件来形成文件夹结构
    files = [
        "async_folder1/file1.txt",
        "async_folder1/file2.txt",
        "async_folder1/subfolder/file3.txt",
        "async_folder2/file4.txt",
    ]

    for file_path in files:
        path = S3Path(
            f"s3://{test_bucket}/{file_path}",
            endpoint_url=s3_config["endpoint_url"],
            region_name=s3_config["region_name"],
            aws_access_key_id=s3_config["aws_access_key_id"],
            aws_secret_access_key=s3_config["aws_secret_access_key"],
        )
        await path.async_write_text("content")

    # 测试文件夹存在（不带尾部斜杠）
    folder1 = S3Path(
        f"s3://{test_bucket}/async_folder1",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert await folder1.async_exists(), "async_folder1 should exist"

    # 测试文件夹存在（带尾部斜杠）
    folder1_slash = S3Path(
        f"s3://{test_bucket}/async_folder1/",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert await folder1_slash.async_exists(), "async_folder1/ should exist"

    # 测试子文件夹存在
    subfolder = S3Path(
        f"s3://{test_bucket}/async_folder1/subfolder",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert await subfolder.async_exists(), "async_folder1/subfolder should exist"

    # 测试不存在的文件夹
    non_existent_folder = S3Path(
        f"s3://{test_bucket}/async_non_existent_folder",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert not await non_existent_folder.async_exists(), (
        "async_non_existent_folder should not exist"
    )

    # 测试文件的 async_exists（确保文件检测仍然正常工作）
    file1 = S3Path(
        f"s3://{test_bucket}/async_folder1/file1.txt",
        endpoint_url=s3_config["endpoint_url"],
        region_name=s3_config["region_name"],
        aws_access_key_id=s3_config["aws_access_key_id"],
        aws_secret_access_key=s3_config["aws_secret_access_key"],
    )
    assert await file1.async_exists(), "async_folder1/file1.txt should exist"
