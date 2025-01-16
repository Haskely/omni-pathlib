# OmniPath

OmniPath 是一个统一的路径处理库，支持本地文件系统、HTTP 和 S3 存储的路径操作。它提供了同步和异步 API，使得在不同存储系统间操作文件变得简单统一。

## 安装

```bash
pip install omni_pathlib
```

## 基本用法

```python
from omni_pathlib import OmniPath

# 创建不同类型的路径
http_path = OmniPath("https://example.com/file.txt")
s3_path = OmniPath("s3://my-bucket/path/to/file.txt")
local_path = OmniPath("/local/path/to/file.txt")

# 读取文件内容
content = http_path.read_text()  # 从 HTTP 读取
s3_content = s3_path.read_text()  # 从 S3 读取
local_content = local_path.read_text()  # 从本地读取

# 异步操作
async def main():
    content = await http_path.async_read_text()
    s3_content = await s3_path.async_read_text()
    local_content = await local_path.async_read_text()
```

## 特性

- 统一的路径操作接口
- 支持本地文件系统、HTTP 和 S3 存储
- 同步和异步 API
- HTTP 支持缓存和断点续传
- S3 支持完整的存储桶操作
- 本地文件系统支持标准的路径操作

## 函数接口说明

### 基础操作

- `exists()` / `async_exists()` - 检查路径是否存在
- `iterdir()` / `async_iterdir()` - 遍历目录内容
- `stat()` / `async_stat()` - 获取文件信息(大小、修改时间等)
- `read_bytes()` / `async_read_bytes()` - 读取文件内容(二进制)
- `read_text()` / `async_read_text()` - 读取文件内容(文本)
- `write_bytes(data)` / `async_write_bytes(data)` - 写入文件内容(二进制)
- `write_text(data)` / `async_write_text(data)` - 写入文件内容(文本)
- `delete()` / `async_delete()` - 删除文件

### 本地文件系统特有操作

- `mkdir(parents=False, exist_ok=False)` / `async_mkdir()` - 创建目录
- `rmdir()` / `async_rmdir()` - 删除空目录
- `rename(target)` / `async_rename(target)` - 重命名文件/目录
- `is_dir()` / `async_is_dir()` - 检查是否为目录
- `is_file()` / `async_is_file()` - 检查是否为文件

### HTTP 特有功能

- 支持断点续传
- 自动缓存下载内容
- 不支持写入和删除操作

### S3 特有功能

- 完整支持 S3 存储桶操作
- 支持自定义 endpoint
- 支持多种认证方式

#### S3 鉴权信息获取逻辑

- 从环境变量 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `OSS_ENDPOINT`, `S3_ENDPOINT`, `AWS_ENDPOINT_URL` 获取环境变量配置
- 从环境变量 `AWS_SHARED_CREDENTIALS_FILE` 获取配置文件路径并加载配置，默认 `~/.aws/credentials`
- 环境变量配置优先级高于配置文件配置
- 从环境变量 `AWS_PROFILE` 获取 profile 名称，默认 `default`
- 若 profile 名称对应的配置不存在，则使用第一个配置名称

## 开发

### 安装依赖

```bash
uv sync
```

### 运行测试

```bash
uv run pytest
```

### commit

```bash
pre-commit install
cz commit
```

### 发布

```bash
cz bump
```
