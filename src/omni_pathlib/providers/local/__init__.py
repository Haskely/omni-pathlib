from omni_pathlib.base_path import BasePath, FileInfo
from pathlib import Path
from anyio import Path as AsyncPath
from datetime import datetime
from typing import Iterator


class LocalPath(BasePath):
    """本地路径类"""

    @property
    def protocol(self) -> str:
        return "file"

    def __init__(self, path: str):
        super().__init__(path)
        self.path_obj = Path(path)
        self.async_path = AsyncPath(path)

    def exists(self) -> bool:
        return self.path_obj.exists()

    async def async_exists(self) -> bool:
        return await self.async_path.exists()

    def iterdir(self) -> Iterator["LocalPath"]:
        for path in self.path_obj.iterdir():
            yield LocalPath(str(path))

    async def async_iterdir(self):
        async for path in self.async_path.iterdir():
            yield LocalPath(str(path))

    def stat(self) -> FileInfo:
        stat = self.path_obj.stat()
        return FileInfo(
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            metadata={
                key: getattr(stat, key) for key in dir(stat) if key.startswith("st_")
            },
        )

    async def async_stat(self) -> FileInfo:
        stat = await self.async_path.stat()
        return FileInfo(
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            metadata={
                key: getattr(stat, key) for key in dir(stat) if key.startswith("st_")
            },
        )

    def read_bytes(self) -> bytes:
        return self.path_obj.read_bytes()

    async def async_read_bytes(self) -> bytes:
        return await self.async_path.read_bytes()

    def read_text(self) -> str:
        return self.path_obj.read_text(encoding="utf-8")

    async def async_read_text(self) -> str:
        return await self.async_path.read_text(encoding="utf-8")

    def write_bytes(self, data: bytes) -> None:
        self.path_obj.write_bytes(data)

    async def async_write_bytes(self, data: bytes) -> int | None:
        await self.async_path.write_bytes(data)
        return None

    def write_text(self, data: str) -> None:
        self.path_obj.write_text(data, encoding="utf-8")

    async def async_write_text(self, data: str) -> int | None:
        await self.async_path.write_text(data, encoding="utf-8")
        return None

    def delete(self) -> None:
        self.path_obj.unlink()

    async def async_delete(self) -> None:
        await self.async_path.unlink()

    def is_dir(self) -> bool:
        return self.path_obj.is_dir()

    async def async_is_dir(self) -> bool:
        return await self.async_path.is_dir()

    def is_file(self) -> bool:
        return self.path_obj.is_file()

    async def async_is_file(self) -> bool:
        return await self.async_path.is_file()

    def mkdir(self, parents: bool = False, exist_ok: bool = False) -> None:
        self.path_obj.mkdir(parents=parents, exist_ok=exist_ok)

    async def async_mkdir(self, parents: bool = False, exist_ok: bool = False) -> None:
        await self.async_path.mkdir(parents=parents, exist_ok=exist_ok)

    def rmdir(self) -> None:
        self.path_obj.rmdir()

    async def async_rmdir(self) -> None:
        await self.async_path.rmdir()

    def rename(self, target: str) -> None:
        self.path_obj.rename(target)

    async def async_rename(self, target: str) -> None:
        await self.async_path.rename(target)
