from omni_pathlib.providers import HttpPath, S3Path, LocalPath
from omni_pathlib.base_path import BasePath
from omni_pathlib.utils.guess_protocol import guess_protocol


def OmniPath(path: str) -> HttpPath | S3Path | LocalPath:
    """智能路径类"""

    path = str(path)
    match protocol := guess_protocol(path):
        case "http":
            return HttpPath(path)
        case "s3":
            return S3Path(path)
        case "file":
            return LocalPath(path)
        case _:
            raise NotImplementedError(f"Unsupported protocol: {protocol}")


__all__ = ["OmniPath", "HttpPath", "S3Path", "LocalPath", "BasePath"]
