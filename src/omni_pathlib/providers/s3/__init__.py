from datetime import datetime
from typing import AsyncIterator, Iterator
from omni_pathlib.base_path import BasePath, FileInfo
from omni_pathlib.providers.s3 import async_ops, sync_ops
import aiohttp
from curl_cffi.requests.exceptions import HTTPError
from omni_pathlib.providers.s3.credentials import DEFAULT_PROFILE_NAME, CREDENTIALS


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

        if profile_name and profile_name not in CREDENTIALS:
            raise ValueError(
                f'Profile "{profile_name}" not found in credentials, avaliable profiles: {list(CREDENTIALS.keys())}'
            )

        _default_profile = CREDENTIALS[profile_name or DEFAULT_PROFILE_NAME]

        if (
            endpoint_url := (endpoint_url or _default_profile.get("endpoint_url"))
        ) is None:
            raise ValueError("Endpoint URL is required")

        if (
            region_name := (region_name or _default_profile.get("region_name"))
        ) is None:
            # print("Region name is not provided! Using default region: us-east-1")
            region_name = "us-east-1"

        if (
            aws_access_key_id := (
                aws_access_key_id or _default_profile.get("aws_access_key_id")
            )
        ) is None:
            raise ValueError("AWS access key ID is required")

        if (
            aws_secret_access_key := (
                aws_secret_access_key or _default_profile.get("aws_secret_access_key")
            )
        ) is None:
            raise ValueError("AWS secret access key is required")

        self.profile_name = profile_name
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

        # 解析 bucket 和 key
        parts = self.path.replace("s3://", "").split("/", 1)
        self.bucket = parts[0]
        self.key = parts[1] if len(parts) > 1 else ""

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
            ),
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
            ),
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

    async def test_listdir():
        path = S3Path("s3://zzx/")

        print("DEBUG: path.async_iterdir()")
        async for item in path.async_iterdir():
            print(item)

        print("DEBUG: path.iterdir()")
        for item in path.iterdir():
            print(item)

    asyncio.run(test_listdir())
