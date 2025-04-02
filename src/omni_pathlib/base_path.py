from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Iterator, TypeVar
from datetime import datetime
from dataclasses import dataclass
from omni_pathlib.utils.join_paths import join_paths
from omni_pathlib.utils.guess_protocol import guess_protocol
from omni_pathlib.utils.parse_url import PathInfo, parse_url
from omni_pathlib.utils.is_absolute_path import is_absolute_path


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
    def path_info(self) -> PathInfo:
        """返回路径信息"""
        return self._path_info

    @property
    def name(self) -> str:
        """返回路径名称"""
        return self.path_info.name

    @property
    def stem(self) -> str:
        """返回路径名称（不带后缀）"""
        return self.path_info.stem

    @property
    def suffix(self) -> str:
        """返回路径后缀"""
        return self.path_info.suffix

    @property
    def parent(self: T) -> T:
        """返回路径父路径"""
        return self.__class__(self.path_info.parent, **self.kwargs)

    @property
    @abstractmethod
    def protocol(self) -> str:
        """返回路径协议（如 'file', 'http', 's3' 等）"""
        pass

    @property
    def kwargs(self) -> dict[str, Any]:
        """返回路径参数"""
        return {}

    def __str__(self) -> str:
        """返回路径字符串"""
        return self.path

    def __truediv__(self: T, other) -> T:
        """实现路径除法运算符 /"""
        other_str = str(other)

        if is_absolute_path(other_str):
            # 如果other是绝对路径，检查协议是否匹配
            other_protocol = guess_protocol(other_str)
            if other_protocol != self.protocol:
                raise ValueError(
                    f"Protocol mismatch: {self.protocol} vs {other_protocol}"
                )
            final_path = other_str
        else:
            # 对于相对路径，进行拼接
            final_path = join_paths(self.path, other_str)

        return self.__class__(final_path, **self.kwargs)

    def __init__(self, path: str) -> None:
        self._path = str(path)
        self._path_info = parse_url(self._path)

    @abstractmethod
    def exists(self) -> bool:
        """检查路径是否存在"""
        pass

    @abstractmethod
    async def async_exists(self) -> bool:
        """异步检查路径是否存在"""
        pass

    @abstractmethod
    def iterdir(self: T) -> Iterator[T]:
        """遍历目录"""
        pass

    @abstractmethod
    def async_iterdir(self: T) -> AsyncIterator[T]:
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
    async def async_write_bytes(self, data: bytes) -> int | None:
        """异步写入文件"""
        pass

    @abstractmethod
    def write_text(self, data: str) -> None:
        """写入文件"""
        pass

    @abstractmethod
    async def async_write_text(self, data: str) -> int | None:
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
