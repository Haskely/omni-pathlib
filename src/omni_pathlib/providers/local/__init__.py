from omni_pathlib.base_path import BasePath, FileInfo
from pathlib import Path
from aiopath import AsyncPath
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

    def async_read_bytes(self):
        return self.async_path.read_bytes()

    def read_text(self) -> str:
        return self.path_obj.read_text(encoding="utf-8")

    def async_read_text(self):
        return self.async_path.read_text(encoding="utf-8")

    def write_bytes(self, data: bytes) -> None:
        self.path_obj.write_bytes(data)

    def async_write_bytes(self, data: bytes):
        return self.async_path.write_bytes(data)

    def write_text(self, data: str) -> None:
        self.path_obj.write_text(data, encoding="utf-8")

    def async_write_text(self, data: str):
        return self.async_path.write_text(data, encoding="utf-8")

    def delete(self) -> None:
        self.path_obj.unlink()

    def async_delete(self):
        return self.async_path.unlink()

    def is_dir(self) -> bool:
        return self.path_obj.is_dir()

    def async_is_dir(self):
        return self.async_path.is_dir()

    def is_file(self) -> bool:
        return self.path_obj.is_file()

    def async_is_file(self):
        return self.async_path.is_file()

    def mkdir(self, parents: bool = False, exist_ok: bool = False):
        self.path_obj.mkdir(parents=parents, exist_ok=exist_ok)

    def async_mkdir(self, parents: bool = False, exist_ok: bool = False):
        return self.async_path.mkdir(parents=parents, exist_ok=exist_ok)

    def rmdir(self):
        self.path_obj.rmdir()

    def async_rmdir(self):
        return self.async_path.rmdir()

    def rename(self, target: str):
        self.path_obj.rename(target)

    def async_rename(self, target: str):
        return self.async_path.rename(target)
