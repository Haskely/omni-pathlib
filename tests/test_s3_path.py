import pytest
from moto.server import ThreadedMotoServer
from omni_pathlib.providers.s3 import S3Path


@pytest.fixture(scope="module")
def moto_server():
    """创建 Moto 服务器实例"""
    server = ThreadedMotoServer()
    server.start()
    yield "http://localhost:5000"
    server.stop()


@pytest.fixture(scope="function")
def test_bucket(moto_server):
    """创建测试用的 bucket"""
    bucket_name = "test-bucket"
    # 使用 S3Path 创建 bucket
    from omni_pathlib.providers.s3.sync_ops import create_bucket

    create_result = create_bucket(bucket_name, moto_server, "", "testing", "testing")
    print("DEBUG: create_result", create_result)

    return bucket_name


@pytest.fixture(scope="function")
def s3_config(moto_server):
    """提供 S3 配置的 fixture"""
    return {
        "endpoint_url": moto_server,
        "region_name": "us-east-1",  # 设置默认 region
        "aws_access_key_id": "testing",
        "aws_secret_access_key": "testing",
    }


def test_s3_path_basic(test_bucket, s3_config):
    """测试 S3Path 的基本功能"""
    path = S3Path(f"s3://{test_bucket}/test.txt", **s3_config)
    path.write_text("测试内容")

    assert path.exists()
    assert path.read_text() == "测试内容"

    # 测试写入操作
    new_path = S3Path(f"s3://{test_bucket}/new.txt", **s3_config)
    new_path.write_text("新内容")
    assert new_path.exists()
    assert new_path.read_text() == "新内容"


@pytest.mark.asyncio
async def test_s3_path_async(test_bucket, s3_config):
    """测试 S3Path 的异步功能"""
    path = S3Path(f"s3://{test_bucket}/async_test.txt", **s3_config)
    await path.async_write_text("异步测试内容")

    assert await path.async_exists()
    assert await path.async_read_text() == "异步测试内容"

    # 测试异步写入
    new_path = S3Path(f"s3://{test_bucket}/async_new.txt", **s3_config)
    await new_path.async_write_text("异步新内容")
    assert await new_path.async_exists()
    assert await new_path.async_read_text() == "异步新内容"


def test_s3_path_iterdir(test_bucket, s3_config):
    """测试目录遍历功能"""
    # 创建测试文件结构
    files = [
        "dir1/file1.txt",
        "dir1/file2.txt",
        "dir2/file3.txt",
        "file4.txt",
        "file5.txt",
    ]

    for file_path in files:
        path = S3Path(f"s3://{test_bucket}/{file_path}", **s3_config)
        path.write_text("content")

    # 测试根目录遍历
    root = S3Path(f"s3://{test_bucket}", **s3_config)
    items = {str(item) for item in root.iterdir()}
    print("DEBUG: items", items)
    target_items = {
        "s3://test-bucket/dir1/",
        "s3://test-bucket/dir2/",
        "s3://test-bucket/file4.txt",
        "s3://test-bucket/file5.txt",
    }
    assert target_items.issubset(items), f"extra items: {target_items - items}"

    # 测试子目录遍历
    dir1 = S3Path(f"s3://{test_bucket}/dir1", **s3_config)
    items = {str(item) for item in dir1.iterdir()}
    print("DEBUG: items", items)
    # FIXME: 这里返回的 items 是空的
    target_items = {
        "s3://test-bucket/dir1/file1.txt",
        "s3://test-bucket/dir1/file2.txt",
    }
    assert target_items.issubset(items), f"extra items: {target_items - items}"


@pytest.mark.asyncio
async def test_s3_path_async_iterdir(test_bucket, s3_config):
    """测试异步目录遍历功能"""
    # 创建测试文件结构
    files = ["async_dir1/file1.txt", "async_dir1/file2.txt", "async_dir2/file3.txt"]
    for file_path in files:
        path = S3Path(f"s3://{test_bucket}/{file_path}", **s3_config)
        path.write_text("content")

    # 测试异步遍历
    root = S3Path(f"s3://{test_bucket}/", **s3_config)
    items = {str(item) async for item in root.async_iterdir()}
    print("DEBUG: items", items)
    target_items = {"s3://test-bucket/async_dir1/", "s3://test-bucket/async_dir2/"}
    assert target_items.issubset(items), f"extra items: {target_items - items}"


def test_s3_path_with_profile_in_scheme(test_bucket, s3_config):
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
    assert path.profile_name == "test_profile"

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
async def test_s3_path_with_profile_in_scheme_async(test_bucket, s3_config):
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
    assert path.profile_name == "async_test_profile"
