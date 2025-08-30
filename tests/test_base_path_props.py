import pytest
from omni_pathlib.providers.local import LocalPath
from pathlib import Path
import os


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


def test_path_properties_consistency(temp_dir: str, test_file: str) -> None:
    """测试路径属性的一致性"""
    path = LocalPath(test_file)
    py_path = Path(test_file)

    # 测试基本路径属性与pathlib.Path一致
    assert path.name == py_path.name, f"name不一致: {path.name} vs {py_path.name}"
    assert path.stem == py_path.stem, f"stem不一致: {path.stem} vs {py_path.stem}"
    assert path.suffix == py_path.suffix, (
        f"suffix不一致: {path.suffix} vs {py_path.suffix}"
    )


def test_path_methods_properties_consistency(temp_dir: str, test_file: str) -> None:
    """测试路径方法后属性的一致性"""
    path = LocalPath(test_file)

    # with_name 操作后属性检查
    new_name = "newfile.doc"
    new_path = path.with_name(new_name)
    assert new_path.name == new_name, (
        f"with_name后name不一致: {new_path.name} vs {new_name}"
    )
    assert new_path.stem == "newfile", (
        f"with_name后stem不一致: {new_path.stem} vs newfile"
    )
    assert new_path.suffix == ".doc", (
        f"with_name后suffix不一致: {new_path.suffix} vs .doc"
    )

    # with_stem 操作后属性检查
    new_stem = "renamed"
    new_path = path.with_stem(new_stem)
    expected_name = f"{new_stem}.txt"
    assert new_path.name == expected_name, (
        f"with_stem后name不一致: {new_path.name} vs {expected_name}"
    )
    assert new_path.stem == new_stem, (
        f"with_stem后stem不一致: {new_path.stem} vs {new_stem}"
    )
    assert new_path.suffix == ".txt", (
        f"with_stem后suffix不一致: {new_path.suffix} vs .txt"
    )

    # with_suffix 操作后属性检查
    new_suffix = ".md"
    new_path = path.with_suffix(new_suffix)
    expected_name = f"test{new_suffix}"
    assert new_path.name == expected_name, (
        f"with_suffix后name不一致: {new_path.name} vs {expected_name}"
    )
    assert new_path.stem == "test", f"with_suffix后stem不一致: {new_path.stem} vs test"
    assert new_path.suffix == new_suffix, (
        f"with_suffix后suffix不一致: {new_path.suffix} vs {new_suffix}"
    )


def test_special_paths(temp_dir: str) -> None:
    """测试特殊路径的属性"""
    # 无后缀文件
    no_suffix_path = LocalPath(os.path.join(temp_dir, "file_without_extension"))
    assert no_suffix_path.name == "file_without_extension"
    assert no_suffix_path.stem == "file_without_extension"
    assert no_suffix_path.suffix == ""

    # 隐藏文件
    hidden_file_path = LocalPath(os.path.join(temp_dir, ".hidden_file"))
    assert hidden_file_path.name == ".hidden_file"
    assert hidden_file_path.stem == ".hidden_file"
    assert hidden_file_path.suffix == ""

    # 带多个点的文件
    multi_dot_path = LocalPath(os.path.join(temp_dir, "file.with.dots.txt"))
    assert multi_dot_path.name == "file.with.dots.txt"
    assert multi_dot_path.stem == "file.with.dots"
    assert multi_dot_path.suffix == ".txt"

    # 目录路径
    dir_path = LocalPath(temp_dir)
    assert dir_path.name == os.path.basename(temp_dir)
    assert dir_path.stem == os.path.basename(temp_dir)
    assert dir_path.suffix == ""


def test_protocol_paths() -> None:
    """测试含协议的路径属性"""
    # HTTP URL 路径
    http_path = LocalPath("http://example.com/path/to/file.txt")
    assert http_path.name == "file.txt"
    assert http_path.stem == "file"
    assert http_path.suffix == ".txt"

    # S3 路径
    s3_path = LocalPath("s3://bucket/folder/document.pdf")
    assert s3_path.name == "document.pdf"
    assert s3_path.stem == "document"
    assert s3_path.suffix == ".pdf"

    # 复杂路径
    complex_path = LocalPath("s3+profile://bucket/path/to/archive.tar.gz")
    assert complex_path.name == "archive.tar.gz"
    assert complex_path.stem == "archive.tar"  # 这里可能与预期不同，要看具体实现
    assert complex_path.suffix == ".gz"
