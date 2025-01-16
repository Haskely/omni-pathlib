import pytest
from omni_pathlib import OmniPath
from omni_pathlib.providers import HttpPath, S3Path, LocalPath


def test_omnipath_protocol_detection():
    """测试 OmniPath 的协议检测功能"""
    # 测试 HTTP 协议
    http_path = OmniPath("http://example.com/test.txt")
    assert isinstance(http_path, HttpPath)
    assert http_path.protocol == "http"

    # 测试 HTTPS 协议
    https_path = OmniPath("https://example.com/test.txt")
    assert isinstance(https_path, HttpPath)
    assert https_path.protocol == "http"

    # 测试 S3 协议
    s3_path = OmniPath("s3://bucket/test.txt")
    assert isinstance(s3_path, S3Path)
    assert s3_path.protocol == "s3"

    # 测试本地文件系统
    local_path = OmniPath("/path/to/file.txt")
    assert isinstance(local_path, LocalPath)
    assert local_path.protocol == "file"

    # 测试相对路径
    relative_path = OmniPath("./file.txt")
    assert isinstance(relative_path, LocalPath)
    assert relative_path.protocol == "file"


def test_omnipath_invalid_protocol():
    """测试无效协议处理"""
    with pytest.raises(NotImplementedError) as exc_info:
        OmniPath("ftp://example.com/test.txt")
    assert "Unsupported protocol" in str(exc_info.value)
