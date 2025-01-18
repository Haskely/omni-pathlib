from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Iterator, TypeVar
from datetime import datetime
from dataclasses import dataclass
from omni_pathlib.utils import join_paths, is_absolute_path
from omni_pathlib.utils.guess_protocol import guess_protocol


@dataclass
class FileInfo:
    """文件信息类"""

    size: int
    modified: datetime | None
    metadata: Any


# 在类定义前添加 TypeVar
T = TypeVar("T", bound="BasePath")


class BasePath(ABC):
    """路径处理器的抽象基类"""

    @property
    def path(self) -> str:
        """返回路径字符串"""
        return self._path

    @property
    @abstractmethod
    def protocol(self) -> str:
        """返回路径协议（如 'file', 'http', 's3' 等）"""
        pass

    def __str__(self) -> str:
        """返回路径字符串"""
        return self.path

    def __truediv__(self: T, other) -> T:
        """实现路径除法运算符 /"""
        other_str = str(other)

        # 如果other是绝对路径，检查协议是否匹配
        if is_absolute_path(other_str):
            other_protocol = guess_protocol(other_str)
            if other_protocol != self.protocol:
                raise ValueError(
                    f"Protocol mismatch: {self.protocol} vs {other_protocol}"
                )
            return self.__class__(other_str)

        # 对于相对路径，进行拼接
        return self.__class__(join_paths(self.path, other_str))

    def __init__(self, path: str) -> None:
        self._path = path

    @abstractmethod
    def exists(self) -> bool:
        """检查路径是否存在"""
        pass

    @abstractmethod
    async def async_exists(self) -> bool:
        """异步检查路径是否存在"""
        pass

    @abstractmethod
    def iterdir(self) -> Iterator["BasePath"]:
        """遍历目录"""
        pass

    @abstractmethod
    def async_iterdir(self) -> AsyncIterator["BasePath"]:
        """异步遍历目录"""
        pass

    @abstractmethod
    def stat(self) -> FileInfo:
        """获取文件信息"""
        pass

    @abstractmethod
    async def async_stat(self) -> FileInfo:
        """异步获取文件信息"""
        pass

    @abstractmethod
    def read_bytes(self) -> bytes:
        """读取文件"""
        pass

    @abstractmethod
    async def async_read_bytes(self) -> bytes:
        """异步读取文件"""
        pass

    @abstractmethod
    def read_text(self) -> str:
        """读取文件"""
        pass

    @abstractmethod
    async def async_read_text(self) -> str:
        """异步读取文件"""
        pass

    @abstractmethod
    def write_bytes(self, data: bytes) -> None:
        """写入文件"""
        pass

    @abstractmethod
    async def async_write_bytes(self, data: bytes) -> None:
        """异步写入文件"""
        pass

    @abstractmethod
    def write_text(self, data: str) -> None:
        """写入文件"""
        pass

    @abstractmethod
    async def async_write_text(self, data: str) -> None:
        """异步写入文件"""
        pass

    @abstractmethod
    def delete(self) -> None:
        """删除文件"""
        pass

    @abstractmethod
    async def async_delete(self) -> None:
        """异步删除文件"""
        pass
