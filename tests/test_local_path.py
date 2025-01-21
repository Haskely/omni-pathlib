import pytest
from omni_pathlib.providers.local import LocalPath
import os
from pathlib import Path


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时目录"""
    return str(tmp_path)


@pytest.fixture
def test_file(temp_dir):
    """创建测试文件"""
    file_path = Path(temp_dir) / "test.txt"
    file_path.write_text("测试内容", encoding="utf-8")
    return str(file_path)


def test_local_path_basic(temp_dir, test_file):
    """测试 LocalPath 的基本功能"""
    # 测试文件操作
    path = LocalPath(test_file)
    assert path.exists()
    assert path.is_file()
    assert not path.is_dir()
    assert path.read_text() == "测试内容"

    # 测试目录操作
    dir_path = LocalPath(temp_dir)
    assert dir_path.exists()
    assert dir_path.is_dir()
    assert not dir_path.is_file()

    # 测试目录遍历
    files = list(dir_path.iterdir())
    assert len(files) == 1
    assert str(files[0]) == test_file


@pytest.mark.asyncio
async def test_local_path_async(temp_dir, test_file):
    """测试 LocalPath 的异步功能"""
    # 测试异步文件操作
    path = LocalPath(test_file)
    assert await path.async_exists()
    assert await path.async_is_file()
    assert not await path.async_is_dir()
    assert await path.async_read_text() == "测试内容"

    # 测试异步目录操作
    dir_path = LocalPath(temp_dir)
    assert await dir_path.async_exists()
    assert await dir_path.async_is_dir()
    assert not await dir_path.async_is_file()

    # 测试异步目录遍历
    files = [f async for f in dir_path.async_iterdir()]
    assert len(files) == 1
    assert str(files[0]) == test_file


def test_local_path_write_operations(temp_dir):
    """测试 LocalPath 的写操作"""
    # 测试写文本文件
    text_file = LocalPath(os.path.join(temp_dir, "write_test.txt"))
    text_file.write_text("新内容")
    assert text_file.exists()
    assert text_file.read_text() == "新内容"

    # 测试写二进制文件
    binary_file = LocalPath(os.path.join(temp_dir, "binary_test.bin"))
    binary_file.write_bytes(b"binary content")
    assert binary_file.exists()
    assert binary_file.read_bytes() == b"binary content"

    # 测试创建目录
    new_dir = LocalPath(os.path.join(temp_dir, "new_dir"))
    new_dir.mkdir()
    assert new_dir.exists()
    assert new_dir.is_dir()

    # 测试删除文件
    text_file.delete()
    assert not text_file.exists()

    # 测试删除目录
    new_dir.rmdir()
    assert not new_dir.exists()


@pytest.mark.asyncio
async def test_local_path_async_write_operations(temp_dir):
    """测试 LocalPath 的异步写操作"""
    # 测试异步写文本文件
    text_file = LocalPath(os.path.join(temp_dir, "async_write_test.txt"))
    await text_file.async_write_text("异步写入")
    assert await text_file.async_exists()
    assert await text_file.async_read_text() == "异步写入"

    # 测试异步写二进制文件
    binary_file = LocalPath(os.path.join(temp_dir, "async_binary_test.bin"))
    await binary_file.async_write_bytes(b"async binary")
    assert await binary_file.async_exists()
    assert await binary_file.async_read_bytes() == b"async binary"

    # 测试异步创建目录
    new_dir = LocalPath(os.path.join(temp_dir, "async_new_dir"))
    await new_dir.async_mkdir()
    assert await new_dir.async_exists()
    assert await new_dir.async_is_dir()

    # 测试异步删除文件
    await text_file.async_delete()
    assert not await text_file.async_exists()

    # 测试异步删除目录
    await new_dir.async_rmdir()
    assert not await new_dir.async_exists()


def test_local_path_join(temp_dir):
    """测试 LocalPath 的路径拼接功能"""
    # 测试基本路径拼接
    base_path = LocalPath(temp_dir)
    sub_path = base_path / "subdir"
    assert str(sub_path) == os.path.join(temp_dir, "subdir")

    # 测试多级路径拼接
    deep_path = base_path / "subdir" / "another" / "deep"
    assert str(deep_path) == os.path.join(temp_dir, "subdir", "another", "deep")

    # 测试与字符串拼接
    str_path = base_path / "test.txt"
    assert str(str_path) == os.path.join(temp_dir, "test.txt")

    # 测试绝对路径拼接（应该返回绝对路径本身）
    abs_path = "/absolute/path"
    result_path = base_path / abs_path
    assert str(result_path) == abs_path

    # 测试相对路径的规范化
    norm_path = base_path / "./subdir" / "../other"
    assert str(norm_path) == os.path.join(temp_dir, "other")

    # 测试连续斜杠的处理
    slash_path = base_path / "subdir/" / "/file.txt"
    assert str(slash_path) == "/file.txt"
