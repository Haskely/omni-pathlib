from datetime import datetime
from typing import AsyncIterator, Iterator
from omni_pathlib.base_path import BasePath, FileInfo
from omni_pathlib.providers.s3 import async_ops, sync_ops
import aiohttp
from curl_cffi.requests.exceptions import HTTPError
from omni_pathlib.providers.s3.credentials import DEFAULT_PROFILE_NAME, CREDENTIALS
from loguru import logger


class S3Path(BasePath):
    @property
    def config(self):
        return {
            "profile_name": self.profile_name,
            "endpoint_url": self.endpoint_url,
            "region_name": self.region_name,
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
        }

    def __init__(
        self,
        path: str,
        profile_name: str | None = None,
        endpoint_url: str | None = None,
        region_name: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ):
        super().__init__(path)

        # 解析 bucket 和 key
        scheme, rest = path.split("://", 1)
        if len(parts := rest.split("/", 1)) == 2:
            self.bucket, self.key = parts
        else:
            self.bucket = rest
            self.key = ""

        # Process Profile Name
        if profile_name and profile_name not in CREDENTIALS:
            raise ValueError(
                f'Profile Name from args: "{profile_name}" not found in credentials, avaliable profile names: {list(CREDENTIALS.keys())}'
            )

        if not profile_name and len(_sch_parts := scheme.split("+")) > 1:
            profile_name = _sch_parts[1]
            if profile_name and profile_name not in CREDENTIALS:
                raise ValueError(
                    f'Profile Name from path scheme({scheme}): "{profile_name}" not found in credentials, avaliable profile names: {list(CREDENTIALS.keys())}'
                )

        if not profile_name:
            profile_name = DEFAULT_PROFILE_NAME

        _profile = CREDENTIALS[profile_name]

        if (endpoint_url := (endpoint_url or _profile.get("endpoint_url"))) is None:
            endpoint_url = "s3.us-east-1.amazonaws.com"
            logger.warning(
                f"Endpoint URL is not provided! Using default endpoint: {endpoint_url}"
            )

        if (region_name := (region_name or _profile.get("region_name"))) is None:
            # print("Region name is not provided! Using default region: us-east-1")
            region_name = "us-east-1"

        if (
            aws_access_key_id := (
                aws_access_key_id or _profile.get("aws_access_key_id")
            )
        ) is None:
            aws_access_key_id = ""
            logger.warning(
                "AWS access key ID is not provided! Using EMPTY access key ID"
            )

        if (
            aws_secret_access_key := (
                aws_secret_access_key or _profile.get("aws_secret_access_key")
            )
        ) is None:
            aws_secret_access_key = ""
            logger.warning(
                "AWS secret access key is not provided! Using EMPTY secret access key"
            )

        self.profile_name = profile_name
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

        self._profile = _profile

    @property
    def protocol(self) -> str:
        return "s3"

    def exists(self) -> bool:
        """检查路径是否存在"""
        try:
            sync_ops.head_object(
                bucket=self.bucket,
                key=self.key,
                endpoint=self.endpoint_url,
                region=self.region_name,
                access_key=self.aws_access_key_id,
                secret_key=self.aws_secret_access_key,
            )
            return True
        except HTTPError as e:
            if e.code == 404:
                return False
            raise

    async def async_exists(self) -> bool:
        """异步检查路径是否存在"""
        try:
            await async_ops.head_object(
                bucket=self.bucket,
                key=self.key,
                endpoint=self.endpoint_url,
                region=self.region_name,
                access_key=self.aws_access_key_id,
                secret_key=self.aws_secret_access_key,
            )
            return True
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                return False
            raise

    def iterdir(self) -> Iterator["BasePath"]:
        """遍历目录"""
        for response in sync_ops.listdir_iter(
            bucket=self.bucket,
            key=self.key,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        ):
            # 处理文件夹
            for prefix in response.get("CommonPrefixes", []):
                if prefix.get("Prefix"):
                    yield S3Path(
                        f"s3://{self.bucket}/{prefix['Prefix']}", **self.config
                    )

            # 处理文件
            for item in response.get("Contents", []):
                if item.get("Key"):
                    yield S3Path(f"s3://{self.bucket}/{item['Key']}", **self.config)

    async def async_iterdir(self) -> AsyncIterator["BasePath"]:
        """异步遍历目录"""
        async for response in async_ops.listdir_iter(
            bucket=self.bucket,
            key=self.key,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        ):
            # 处理文件夹
            for prefix in response.get("CommonPrefixes", []):
                if prefix.get("Prefix"):
                    yield S3Path(
                        f"s3://{self.bucket}/{prefix['Prefix']}", **self.config
                    )

            # 处理文件
            for item in response.get("Contents", []):
                if item.get("Key"):
                    yield S3Path(f"s3://{self.bucket}/{item['Key']}", **self.config)

    def stat(self) -> FileInfo:
        """获取文件信息"""
        metadata = sync_ops.head_object(
            bucket=self.bucket,
            key=self.key,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )
        return FileInfo(
            size=metadata["ContentLength"],
            modified=datetime.strptime(
                metadata["LastModified"], "%a, %d %b %Y %H:%M:%S %Z"
            )
            if metadata["LastModified"]
            else None,
            metadata=metadata,
        )

    async def async_stat(self) -> FileInfo:
        """异步获取文件信息"""
        metadata = await async_ops.head_object(
            bucket=self.bucket,
            key=self.key,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )
        return FileInfo(
            size=metadata["ContentLength"],
            modified=datetime.strptime(
                metadata["LastModified"], "%a, %d %b %Y %H:%M:%S %Z"
            )
            if metadata["LastModified"]
            else None,
            metadata=metadata,
        )

    def read_bytes(self) -> bytes:
        """读取文件内容（字节）"""
        return sync_ops.download_file(
            bucket=self.bucket,
            key=self.key,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )

    async def async_read_bytes(self) -> bytes:
        """异步读取文件内容（字节）"""
        return await async_ops.download_file(
            bucket=self.bucket,
            key=self.key,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )

    def read_text(self) -> str:
        """读取文件内容（文本）"""
        return self.read_bytes().decode("utf-8")

    async def async_read_text(self) -> str:
        """异步读取文件内容（文本）"""
        content = await self.async_read_bytes()
        return content.decode("utf-8")

    def write_bytes(self, data: bytes) -> None:
        """写入文件内容（字节）"""
        sync_ops.upload_file(
            bucket=self.bucket,
            key=self.key,
            data=data,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )

    async def async_write_bytes(self, data: bytes) -> None:
        """异步写入文件内容（字节）"""
        await async_ops.upload_file(
            bucket=self.bucket,
            key=self.key,
            data=data,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )

    def write_text(self, data: str) -> None:
        """写入文件内容（文本）"""
        self.write_bytes(data.encode("utf-8"))

    async def async_write_text(self, data: str) -> None:
        """异步写入文件内容（文本）"""
        await self.async_write_bytes(data.encode("utf-8"))

    def delete(self) -> None:
        """删除文件"""
        sync_ops.delete_object(
            bucket=self.bucket,
            key=self.key,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )

    async def async_delete(self) -> None:
        """异步删除文件"""
        await async_ops.delete_object(
            bucket=self.bucket,
            key=self.key,
            endpoint=self.endpoint_url,
            region=self.region_name,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )


if __name__ == "__main__":
    import asyncio

    from rich import print

    async def test_scheme_profile():
        path = S3Path("s3+test_profile://test-bucket/profile_test.txt")
        print(path.config)

    asyncio.run(test_scheme_profile())
