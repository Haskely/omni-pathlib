# Omni-Pathlib

[English Documentation](README.md)

[![PyPI version](https://img.shields.io/pypi/v/omni-pathlib.svg)](https://pypi.org/project/omni-pathlib/)
[![Python Version](https://img.shields.io/pypi/pyversions/omni-pathlib.svg)](https://pypi.org/project/omni-pathlib/)
[![License](https://img.shields.io/github/license/Haskely/omni-pathlib.svg)](https://github.com/Haskely/omni-pathlib/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/omni-pathlib)](https://pepy.tech/project/omni-pathlib)
[![GitHub Stars](https://img.shields.io/github/stars/Haskely/omni-pathlib.svg)](https://github.com/Haskely/omni-pathlib/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Haskely/omni-pathlib.svg)](https://github.com/Haskely/omni-pathlib/issues)
[![Dependencies](https://img.shields.io/librariesio/github/Haskely/omni-pathlib)](https://libraries.io/github/Haskely/omni-pathlib)

Omni-Pathlib 是一个统一的路径处理库，支持本地文件系统、HTTP 和 S3 存储的路径操作。它提供了同步和异步 API，使得在不同存储系统间操作文件变得简单统一。

## 安装

```bash
pip install omni-pathlib
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

所有存储类型都支持以下操作：

```python
# 路径属性
path.name      # 获取路径名称
path.stem      # 获取不带后缀的路径名称
path.suffix    # 获取路径后缀
path.parent    # 获取父路径
path.protocol  # 获取协议类型（'file'、'http'、's3'）

# 基础操作
path.exists()             # 检查路径是否存在
path.iterdir()            # 遍历目录内容
path.stat()               # 获取文件信息（大小、修改时间等）
path.read_bytes()         # 读取二进制内容
path.read_text()          # 读取文本内容
path.write_bytes(data)    # 写入二进制内容
path.write_text(data)     # 写入文本内容
path.delete()             # 删除文件

# 所有操作都有对应的异步版本
await path.async_exists()
await path.async_iterdir()
# ... 等等
```

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
- 支持在 URL scheme 中指定 profile

#### S3 Profile 配置优先级

配置优先级从高到低：

1. 通过参数直接传入的配置
2. 通过 URL scheme 指定的 profile（例如：`s3+my_profile://bucket/key`）
3. 通过环境变量 `AWS_PROFILE` 配置
4. 配置文件中的 `default` profile
5. 配置文件中的第一个 profile

#### S3 URL Scheme 示例

```python
# 参数优先级高于 URL scheme
path = OmniPath(
    "s3+my_profile://bucket/key",
    profile_name="other_profile"  # 将使用 other_profile 而不是 my_profile
)

# 通过 URL scheme 指定 profile
path = OmniPath("s3+my_profile://bucket/key")  # 将使用 my_profile 配置

# 通过环境变量指定 profile
os.environ["AWS_PROFILE"] = "other_profile"
path = OmniPath("s3://bucket/key")  # 将使用 other_profile 配置

# 通过配置文件指定 profile
path = OmniPath("s3://bucket/key")  # 将使用 default 配置（如果存在）或者找到的第一个配置
```

#### S3 Profiles 获取逻辑

- 从环境变量 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `OSS_ENDPOINT`, `S3_ENDPOINT`, `AWS_ENDPOINT_URL` 获取环境变量配置，这些配置默认会覆盖到名为 `default` profile 中，但是可以通过添加前缀指定到其他名字的 profile 中，例如：`my_profile__AWS_ACCESS_KEY_ID=my_access_key_id` 会放到名为 `my_profile` 的 profile 中
- 从环境变量 `AWS_SHARED_CREDENTIALS_FILE` 获取配置文件路径并加载配置，默认 `~/.aws/credentials`

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

git push
git push --tags
```
