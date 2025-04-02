import pytest
from pytest_httpserver import HTTPServer
from omni_pathlib.providers.http import HttpPath
import os
from datetime import datetime


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("localhost", 0)


@pytest.fixture
def test_content():
    return b"Hello, World!"


@pytest.fixture
def mock_server(httpserver: HTTPServer, test_content):
    """配置测试服务器"""
    # 模拟基本的 GET 请求
    httpserver.expect_request("/test.txt").respond_with_data(
        test_content,
        headers={
            "content-length": str(len(test_content)),
            "last-modified": "Wed, 21 Oct 2023 07:28:00 GMT",
            "accept-ranges": "bytes",
        },
    )

    # 模拟支持断点续传的大文件
    large_content = b"Large " * 8192
    httpserver.expect_request("/large.txt", method="HEAD").respond_with_data(
        "",
        headers={"content-length": str(len(large_content)), "accept-ranges": "bytes"},
    )

    # 修改 GET 请求的配置
    httpserver.expect_request("/large.txt", method="GET").respond_with_data(
        large_content,
        headers={"content-length": str(len(large_content)), "accept-ranges": "bytes"},
    )

    return httpserver


def test_http_path_basic(mock_server, test_content):
    """测试 HttpPath 的基本功能"""
    url = f"http://{mock_server.host}:{mock_server.port}/test.txt"
    path = HttpPath(url)

    # 测试存在性检查
    assert path.exists()

    # 测试读取内容
    assert path.read_bytes() == test_content
    assert path.read_text() == test_content.decode()

    # 测试文件信息
    info = path.stat()
    assert info.size == len(test_content)
    assert isinstance(info.modified, datetime)


@pytest.mark.asyncio
async def test_http_path_async(mock_server, test_content):
    """测试 HttpPath 的异步功能"""
    url = f"http://{mock_server.host}:{mock_server.port}/test.txt"
    path = HttpPath(url)

    # 测试异步存在性检查
    assert await path.async_exists()

    # 测试异步读取
    assert await path.async_read_bytes() == test_content
    assert await path.async_read_text() == test_content.decode()

    # 测试异步文件信息
    info = await path.async_stat()
    assert info.size == len(test_content)
    assert isinstance(info.modified, datetime)


def test_http_path_cache(mock_server, test_content, tmp_path):
    """测试 HTTP 缓存功能"""
    url = f"http://{mock_server.host}:{mock_server.port}/test.txt"
    cache_dir = str(tmp_path / "http_cache")
    path = HttpPath(url, cache_dir=cache_dir)

    # 第一次下载
    content1 = path.read_bytes()
    assert content1 == test_content

    # 验证缓存文件存在
    cache_files = os.listdir(cache_dir)
    assert len(cache_files) == 1

    # 第二次读取应该从缓存获取
    content2 = path.read_bytes()
    assert content2 == test_content

    # 请求计数应该是 2（有 HEAD 和 GET 两个请求）
    assert len(mock_server.log) == 2
    assert mock_server.log[0][0].method == "HEAD"
    assert mock_server.log[1][0].method == "GET"


def test_http_path_range_download(mock_server, tmp_path):
    """测试断点续传功能"""
    url = f"http://{mock_server.host}:{mock_server.port}/large.txt"
    cache_dir = str(tmp_path / "http_cache")
    path = HttpPath(url, cache_dir=cache_dir)

    # 下载文件
    content = path.read_bytes()
    assert content.startswith(b"Large ")
    assert len(content) == 6 * 8192  # "Large " 是 6 字节，重复 8192 次


@pytest.mark.asyncio
async def test_http_path_range_download_async(mock_server, tmp_path):
    """测试断点续传功能"""
    url = f"http://{mock_server.host}:{mock_server.port}/large.txt"
    cache_dir = str(tmp_path / "http_cache")
    path = HttpPath(url, cache_dir=cache_dir)

    # 下载文件
    content2 = await path.async_read_bytes()
    assert content2.startswith(b"Large ")
    assert len(content2) == 6 * 8192  # "Large " 是 6 字节，重复 8192 次


def test_http_path_unsupported_operations(mock_server):
    """测试不支持的操作"""
    url = f"http://{mock_server.host}:{mock_server.port}/test.txt"
    path = HttpPath(url)

    with pytest.raises(NotImplementedError):
        path.write_bytes(b"data")

    with pytest.raises(NotImplementedError):
        path.write_text("data")

    with pytest.raises(NotImplementedError):
        path.delete()

    with pytest.raises(NotImplementedError):
        path.iterdir()
