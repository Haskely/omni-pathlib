"""
AWS 配置文件和环境变量解析

- 从 AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, OSS_ENDPOINT, S3_ENDPOINT, AWS_ENDPOINT_URL 获取环境变量配置
- 从 AWS_SHARED_CREDENTIALS_FILE 获取配置文件路径并加载配置，默认 ~/.aws/credentials
- 环境变量配置优先级高于配置文件配置
- 从 AWS_PROFILE 获取 profile 名称，默认 default
- 若 profile 名称对应的配置不存在，则使用第一个配置名称
"""

from collections import defaultdict
import configparser
import os
from rich import print
import logging

logger = logging.getLogger(__name__)

env_name_map = {
    "aws_access_key_id": ("AWS_ACCESS_KEY_ID",),
    "aws_secret_access_key": ("AWS_SECRET_ACCESS_KEY",),
    "region": ("AWS_REGION",),
    "endpoint_url": ("OSS_ENDPOINT", "S3_ENDPOINT", "AWS_ENDPOINT_URL"),
}


def get_credentials_from_env():
    credentials: dict[str, dict[str, str]] = defaultdict(dict)
    for key, value in os.environ.items():
        for name, suffixes in env_name_map.items():
            for suffix in suffixes:
                if key.endswith(suffix):
                    if "__" in key:
                        profile_name = key.split("__")[0]
                        credentials[profile_name][name] = value
                    else:
                        credentials["default"][name] = value
    return credentials


def read_config(filename):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(filename)
    return {section: dict(config.items(section)) for section in config.sections()}


def get_credentials_from_file(config_path: str):
    config = read_config(config_path)

    credentials = {}
    for section_name, section_data in config.items():
        if "s3" in section_data:
            s3_config = section_data["s3"]
            for line in s3_config.split("\n"):
                if "=" in line:
                    key, value = line.split("=", maxsplit=1)
                    section_data[key.strip()] = value.strip()

        if "region" in section_data:
            section_data["region_name"] = section_data["region"]

        credentials[section_name] = section_data
    return credentials


CREDENTIALS_PATH = os.getenv(
    "AWS_SHARED_CREDENTIALS_FILE", os.path.expanduser("~/.aws/credentials")
)
ENV_CREDENTIALS = get_credentials_from_env()
FILE_CREDENTIALS = get_credentials_from_file(CREDENTIALS_PATH)

CREDENTIALS = ENV_CREDENTIALS | FILE_CREDENTIALS
DEFAULT_PROFILE_NAME = os.getenv("AWS_PROFILE", "default")

# 添加默认配置，确保至少有一个可用的 profile
if not CREDENTIALS:
    CREDENTIALS["default"] = {}
    logger.warning("No AWS credentials found, using empty default profile")

if DEFAULT_PROFILE_NAME not in CREDENTIALS:
    first_profile_name = next(iter(CREDENTIALS.keys()))
    logger.warning(
        f'Profile "{DEFAULT_PROFILE_NAME}" not found in credentials, using first profile "{first_profile_name}"'
    )
    DEFAULT_PROFILE_NAME = first_profile_name

if __name__ == "__main__":
    print(CREDENTIALS)
    print(DEFAULT_PROFILE_NAME)
