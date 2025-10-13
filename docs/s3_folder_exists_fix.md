# S3 文件夹 exists 检测修复

## 问题描述

在 S3 存储中，文件夹（目录）并不是真正的对象，而只是路径前缀。原有的 `exists()` 方法仅使用 `HEAD` 请求检查路径是否存在，这对文件有效，但对文件夹会返回 404 错误，导致无法正确检测文件夹是否存在。

## 问题示例

```python
# 假设 s3://bucket/folder1/ 下有文件
path = S3Path("s3://bucket/folder1")
path.exists()  # 返回 False（错误！）
```

## 解决方案

修改 `exists()` 和 `async_exists()` 方法的实现逻辑：

1. **先尝试作为文件检查**：使用 `HEAD` 请求检查是否为文件
2. **如果 404，再尝试作为文件夹检查**：使用 `LIST` 请求检查是否有以该路径为前缀的对象

### 修改的文件

- [`src/omni_pathlib/providers/s3/__init__.py`](../src/omni_pathlib/providers/s3/__init__.py)
  - [`exists()`](../src/omni_pathlib/providers/s3/__init__.py:114) 方法
  - [`async_exists()`](../src/omni_pathlib/providers/s3/__init__.py:131) 方法

### 实现细节

```python
def exists(self) -> bool:
    """检查路径是否存在（文件或文件夹）"""
    # 1. 先尝试作为文件检查（使用 HEAD 请求）
    try:
        sync_ops.head_object(...)
        return True
    except HTTPError as e:
        if e.response is not None and cast(Response, e.response).status_code == 404:
            # 2. 如果文件不存在，尝试作为文件夹检查（使用 LIST 请求）
            prefix = self.key if self.key.endswith("/") else f"{self.key}/"
            response = sync_ops.list_objects(
                ...,
                prefix=prefix,
                max_keys=1,  # 只需要检查是否有对象，1个就够了
            )
            # 如果有任何对象或子文件夹，则认为该文件夹存在
            return response.get("KeyCount", 0) > 0
        raise
```

## 测试覆盖

新增了完整的测试用例：

- [`test_s3_folder_exists()`](../tests/test_s3_path.py:350)：同步版本的文件夹存在性检测
- [`test_s3_folder_async_exists()`](../tests/test_s3_path.py:423)：异步版本的文件夹存在性检测

测试场景包括：
- 文件夹存在（不带尾部斜杠）
- 文件夹存在（带尾部斜杠）
- 子文件夹存在
- 不存在的文件夹
- 文件的 exists 检测（确保向后兼容）

## 性能考虑

- 对于文件，性能与之前完全相同（单次 HEAD 请求）
- 对于文件夹，需要额外的 LIST 请求（仅在 HEAD 返回 404 时）
- LIST 请求使用 `max_keys=1` 参数优化，只需要检查是否有对象，无需获取完整列表

## 验证

所有测试通过：

```bash
uv run pytest tests/test_s3_path.py -v
# 10 passed in 1.31s
