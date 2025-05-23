# Omni-Pathlib

[中文文档](README_ZH.md)

[![PyPI version](https://img.shields.io/pypi/v/omni-pathlib.svg)](https://pypi.org/project/omni-pathlib/)
[![Python Version](https://img.shields.io/pypi/pyversions/omni-pathlib.svg)](https://pypi.org/project/omni-pathlib/)
[![License](https://img.shields.io/github/license/Haskely/omni-pathlib.svg)](https://github.com/Haskely/omni-pathlib/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/omni-pathlib)](https://pepy.tech/project/omni-pathlib)
[![GitHub Stars](https://img.shields.io/github/stars/Haskely/omni-pathlib.svg)](https://github.com/Haskely/omni-pathlib/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Haskely/omni-pathlib.svg)](https://github.com/Haskely/omni-pathlib/issues)
[![Dependencies](https://img.shields.io/librariesio/github/Haskely/omni-pathlib)](https://libraries.io/github/Haskely/omni-pathlib)

Omni-Pathlib is a unified path handling library that supports path operations for local file systems, HTTP, and S3 storage. It provides both synchronous and asynchronous APIs, making it easy and consistent to operate files across different storage systems.

## Installation

```bash
pip install omni-pathlib
```

## Basic Usage

```python
from omni_pathlib import OmniPath

# Create different types of paths
http_path = OmniPath("https://example.com/file.txt")
s3_path = OmniPath("s3://my-bucket/path/to/file.txt")
local_path = OmniPath("/local/path/to/file.txt")

# Read file content
content = http_path.read_text()  # Read from HTTP
s3_content = s3_path.read_text()  # Read from S3
local_content = local_path.read_text()  # Read from local

# Asynchronous operations
async def main():
    content = await http_path.async_read_text()
    s3_content = await s3_path.async_read_text()
    local_content = await local_path.async_read_text()
```

## Features

- Unified path operation interface
- Supports local file systems, HTTP, and S3 storage
- Synchronous and asynchronous APIs
- HTTP supports caching and resuming downloads
- S3 supports complete bucket operations
- Local file system supports standard path operations

## Function Interface Description

### Basic Operations

All storage types support the following operations:

```python
# Path attributes
path.name      # Get the path name
path.stem      # Get the path name without suffix
path.suffix    # Get the path suffix
path.parent    # Get the parent path
path.protocol  # Get the protocol type ('file', 'http', 's3')

# Basic operations
path.exists()             # Check if the path exists
path.iterdir()            # Iterate through directory contents
path.stat()               # Get file information (size, modification time, etc.)
path.read_bytes()         # Read binary content
path.read_text()          # Read text content
path.write_bytes(data)    # Write binary content
path.write_text(data)     # Write text content
path.delete()             # Delete file

# All operations have corresponding asynchronous versions
await path.async_exists()
await path.async_iterdir()
# ... and so on
```

### Local File System Specific Operations

- `mkdir(parents=False, exist_ok=False)` / `async_mkdir()` - Create a directory
- `rmdir()` / `async_rmdir()` - Remove an empty directory
- `rename(target)` / `async_rename(target)` - Rename a file/directory
- `is_dir()` / `async_is_dir()` - Check if it is a directory
- `is_file()` / `async_is_file()` - Check if it is a file

### HTTP Specific Features

- Supports resuming downloads
- Automatically caches downloaded content
- Does not support write and delete operations

### S3 Specific Features

- Fully supports S3 bucket operations
- Supports custom endpoints
- Supports multiple authentication methods
- Supports specifying profile in URL scheme

#### S3 Profile Configuration Priority

Configuration priority from high to low:

1. Configuration passed directly as parameters
2. Profile specified in URL scheme (e.g., `s3+my_profile://bucket/key`)
3. Configuration through environment variable `AWS_PROFILE`
4. `default` profile in configuration file
5. The first profile found in the configuration file

#### S3 URL Scheme Example

```python
# Parameter priority is higher than URL scheme
path = OmniPath(
    "s3+my_profile://bucket/key",
    profile_name="other_profile"  # Will use other_profile instead of my_profile
)

# Specify profile through URL scheme
path = OmniPath("s3+my_profile://bucket/key")  # Will use my_profile configuration

# Specify profile through environment variable
os.environ["AWS_PROFILE"] = "other_profile"
path = OmniPath("s3://bucket/key")  # Will use other_profile configuration

# Specify profile through configuration file
path = OmniPath("s3://bucket/key")  # Will use default configuration (if exists) or the first found configuration
```

#### S3 Profiles Retrieval Logic

- Retrieve environment variable configurations from `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `OSS_ENDPOINT`, `S3_ENDPOINT`, `AWS_ENDPOINT_URL`. These configurations will default to the `default` profile but can be specified to other named profiles by adding a prefix, e.g., `my_profile__AWS_ACCESS_KEY_ID=my_access_key_id` will go into the profile named `my_profile`.
- Load configurations from the configuration file path obtained from the environment variable `AWS_SHARED_CREDENTIALS_FILE`, defaulting to `~/.aws/credentials`.

## Development

### Install Dependencies

```bash
uv sync
```

### Run Tests

```bash
uv run pytest
```

### Commit

```bash
pre-commit install
cz commit
```

### Release

```bash
cz bump

git push
git push --tags
```
