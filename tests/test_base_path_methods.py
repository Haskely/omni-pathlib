import pytest
from omni_pathlib.providers.local import LocalPath
import os
from pathlib import Path


@pytest.fixture
def temp_dir(tmp_path: Path) -> str:
    """创建临时目录"""
    return str(tmp_path)


@pytest.fixture
def test_file(temp_dir: str) -> str:
    """创建测试文件"""
    file_path = Path(temp_dir) / "test.txt"
    file_path.write_text("测试内容", encoding="utf-8")
    return str(file_path)


def test_with_name(temp_dir: str, test_file: str) -> None:
    """测试 with_name 方法"""
    path = LocalPath(test_file)

    # 测试基本功能
    new_path = path.with_name("new_name.txt")
    assert new_path.name == "new_name.txt"
    assert new_path.stem == "new_name"
    assert new_path.suffix == ".txt"
    assert new_path.parent.path == path.parent.path

    # 测试更改文件后缀
    new_path = path.with_name("document.pdf")
    assert new_path.name == "document.pdf"
    assert new_path.stem == "document"
    assert new_path.suffix == ".pdf"

    # 测试错误情况
    with pytest.raises(ValueError):
        path.with_name("")


def test_with_stem(temp_dir: str, test_file: str) -> None:
    """测试 with_stem 方法"""
    path = LocalPath(test_file)

    # 测试基本功能
    new_path = path.with_stem("new_stem")
    assert new_path.name == "new_stem.txt"
    assert new_path.stem == "new_stem"
    assert new_path.suffix == ".txt"
    assert new_path.parent.path == path.parent.path

    # 测试更改为无后缀的文件名
    path_no_suffix = LocalPath(os.path.join(temp_dir, "file_without_extension"))
    Path(str(path_no_suffix)).touch()

    new_path = path_no_suffix.with_stem("renamed")
    assert new_path.name == "renamed"
    assert new_path.stem == "renamed"
    assert new_path.suffix == ""

    # 测试错误情况
    with pytest.raises(ValueError):
        path.with_stem("")


def test_with_suffix(temp_dir: str, test_file: str) -> None:
    """测试 with_suffix 方法"""
    path = LocalPath(test_file)

    # 获取测试路径的本地信息
    Path(test_file).name
    original_stem = Path(test_file).stem

    # 测试基本功能（提供带点的后缀）
    new_path = path.with_suffix(".md")
    new_path_obj = Path(new_path.path)
    assert new_path_obj.name == f"{original_stem}.md"
    assert new_path.parent.path == path.parent.path

    # 测试提供不带点的后缀
    new_path = path.with_suffix("pdf")
    new_path_obj = Path(new_path.path)
    assert new_path_obj.name == f"{original_stem}.pdf"

    # 测试清除后缀
    new_path = path.with_suffix("")
    new_path_obj = Path(new_path.path)
    assert new_path_obj.name == original_stem

    # 测试添加后缀到无后缀文件
    path_no_suffix = LocalPath(os.path.join(temp_dir, "file_without_extension"))
    Path(str(path_no_suffix)).touch()

    no_suffix_stem = "file_without_extension"
    new_path = path_no_suffix.with_suffix(".txt")
    new_path_obj = Path(new_path.path)
    assert new_path_obj.name == f"{no_suffix_stem}.txt"


def test_method_chaining(temp_dir: str, test_file: str) -> None:
    """测试方法链式调用"""
    path = LocalPath(test_file)

    # 测试多个方法链式调用
    new_path = path.with_name("document.pdf").with_stem("report").with_suffix(".docx")
    assert new_path.name == "report.docx"
    assert new_path.stem == "report"
    assert new_path.suffix == ".docx"


def test_path_identity(temp_dir: str, test_file: str) -> None:
    """测试路径身份保持（确保返回的是相同类型的路径对象）"""
    path = LocalPath(test_file)

    # 测试返回的对象类型与原始对象相同
    new_path = path.with_name("new_file.txt")
    assert isinstance(new_path, LocalPath)

    new_path = path.with_stem("new_stem")
    assert isinstance(new_path, LocalPath)

    new_path = path.with_suffix(".new")
    assert isinstance(new_path, LocalPath)


@pytest.mark.asyncio
async def test_async_path_operations(temp_dir: str, test_file: str) -> None:
    """测试异步方法可以与新方法一起正确工作"""
    path = LocalPath(test_file)

    # 测试 with_name 方法生成的路径与异步读写
    new_path = path.with_name("async_test.txt")
    await new_path.async_write_text("异步写入测试")
    content = await new_path.async_read_text()
    assert content == "异步写入测试"

    # 测试 with_stem 方法生成的路径与异步读写
    stem_path = new_path.with_stem("async_renamed")
    await stem_path.async_write_text("新名称测试")
    content = await stem_path.async_read_text()
    assert content == "新名称测试"

    # 测试 with_suffix 方法生成的路径与异步读写
    suffix_path = stem_path.with_suffix(".md")
    await suffix_path.async_write_text("后缀测试")
    content = await suffix_path.async_read_text()
    assert content == "后缀测试"

    # 清理测试创建的文件
    await new_path.async_delete()
    await stem_path.async_delete()
    await suffix_path.async_delete()
