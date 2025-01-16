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

### S3 鉴权信息获取逻辑

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
cz commit
```

### 发布

```bash
cz release
```
