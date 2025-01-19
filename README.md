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

git push --follow-tags
```
