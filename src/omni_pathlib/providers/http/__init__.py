from omni_pathlib.base_path import BasePath, FileInfo
from curl_cffi import requests
from datetime import datetime
from omni_pathlib.providers.local import LocalPath
import os
import hashlib
from typing import Optional, Tuple

from omni_pathlib.utils.raise_for_status_with_text import (
    curl_cffi_raise_for_status_with_text,
)


class HttpPath(BasePath):
    @property
    def protocol(self) -> str:
        return "http"

    def __init__(self, path: str, cache_dir: Optional[str] = None):
        super().__init__(path)
        self.session = requests.Session()
        self.async_session = requests.AsyncSession()
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.cache/omni_pathlib")
        self._cache_dir = LocalPath(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def close(self):
        self.session.close()
        _ = self.async_session.close()

    def _get_cache_path(self) -> Tuple[LocalPath, LocalPath]:
        """获取缓存文件路径和临时文件路径"""
        path_hash = hashlib.md5(self.path.encode()).hexdigest()
        cache_path = self._cache_dir / f"{path_hash}.bytes"
        temp_path = self._cache_dir / f"{path_hash}.bytes.part"
        return cache_path, temp_path

    def _supports_range(self, response: requests.Response) -> bool:
        """检查服务器是否支持断点续传"""
        return "accept-ranges" in response.headers

    def exists(self) -> bool:
        try:
            response = self.session.head(self.path)
            return response.status_code == 200
        except requests.RequestsError:
            return False

    async def async_exists(self) -> bool:
        try:
            response = await self.async_session.head(self.path)
            return response.status_code == 200
        except requests.RequestsError:
            return False

    def iterdir(self):  # type: ignore
        raise NotImplementedError(f"{self.path} does not support iterdir")

    async def async_iterdir(self):  # type: ignore
        raise NotImplementedError(f"{self.path} does not support async_iterdir")

    def stat(self) -> FileInfo:
        response = self.session.head(self.path)
        curl_cffi_raise_for_status_with_text(response)

        return FileInfo(
            size=int(response.headers.get("content-length", 0)),
            modified=datetime.strptime(
                response.headers.get("last-modified", ""), "%a, %d %b %Y %H:%M:%S GMT"
            )
            if "last-modified" in response.headers
            else datetime.now(),
            metadata=dict(response.headers),
        )

    async def async_stat(self) -> FileInfo:
        response = await self.async_session.head(self.path)
        curl_cffi_raise_for_status_with_text(response)

        return FileInfo(
            size=int(response.headers.get("content-length", 0)),
            modified=datetime.strptime(
                response.headers.get("last-modified", ""),
                "%a, %d %b %Y %H:%M:%S GMT",
            )
            if "last-modified" in response.headers
            else datetime.now(),
            metadata=dict(response.headers),
        )

    def download(self) -> bytes:
        cache_path, temp_path = self._get_cache_path()

        # 检查完整缓存是否存在
        if cache_path.exists():
            return cache_path.read_bytes()

        # 检查是否存在未完成的下载
        initial_pos = temp_path.stat().size if temp_path.exists() else 0

        # 先发送 HEAD 请求获取文件信息
        head_resp = self.session.head(self.path)
        curl_cffi_raise_for_status_with_text(head_resp)

        if self._supports_range(head_resp):
            # 支持断点续传的情况
            headers = {"Range": f"bytes={initial_pos}-"} if initial_pos > 0 else {}
            with self.session.stream("GET", self.path, headers=headers) as response:
                response.raise_for_status()

                with open(temp_path.path, "ab" if initial_pos > 0 else "wb") as f:
                    for chunk in response.iter_content(
                        chunk_size=None
                    ):  # UserWarning: chunk_size is ignored, there is no way to tell curl that.
                        f.write(chunk)

            # 下载完成，重命名为正式缓存文件
            temp_path.rename(cache_path.path)
            return cache_path.read_bytes()
        else:
            # 不支持断点续传，直接下载
            response = self.session.get(self.path)
            response.raise_for_status()
            cache_path.write_bytes(response.content)
            return response.content

    async def async_download(self) -> bytes:
        cache_path, temp_path = self._get_cache_path()

        # 检查完整缓存是否存在
        if cache_path.exists():
            return cache_path.read_bytes()

        # 检查是否存在未完成的下载
        initial_pos = temp_path.stat().size if temp_path.exists() else 0

        # 先发送 HEAD 请求获取文件信息
        head_resp = await self.async_session.head(self.path)
        head_resp.raise_for_status()

        if self._supports_range(head_resp):
            # 支持断点续传的情况
            headers = {"Range": f"bytes={initial_pos}-"} if initial_pos > 0 else {}
            response = await self.async_session.get(
                self.path, headers=headers, stream=True
            )
            response.raise_for_status()

            with open(temp_path.path, "ab" if initial_pos > 0 else "wb") as f:
                async for chunk in response.aiter_content():
                    f.write(chunk)

            # 下载完成，重命名为正式缓存文件
            temp_path.rename(cache_path.path)
            return cache_path.read_bytes()
        else:
            # 不支持断点续传，直接下载
            response = await self.async_session.get(self.path)
            response.raise_for_status()
            cache_path.write_bytes(response.content)
            return response.content

    def read_bytes(self) -> bytes:
        return self.download()

    async def async_read_bytes(self) -> bytes:
        return await self.async_download()

    def read_text(self) -> str:
        return self.download().decode()

    async def async_read_text(self) -> str:
        content = await self.async_download()
        return content.decode()

    def write_bytes(self, data: bytes) -> None:
        raise NotImplementedError(f"{self.path} does not support write_bytes")

    async def async_write_bytes(self, data: bytes) -> None:
        raise NotImplementedError(f"{self.path} does not support async_write_bytes")

    def write_text(self, data: str) -> None:
        raise NotImplementedError(f"{self.path} does not support write_text")

    async def async_write_text(self, data: str) -> None:
        raise NotImplementedError(f"{self.path} does not support async_write_text")

    def delete(self) -> None:
        raise NotImplementedError(f"{self.path} does not support delete")

    async def async_delete(self) -> None:
        raise NotImplementedError(f"{self.path} does not support async_delete")
