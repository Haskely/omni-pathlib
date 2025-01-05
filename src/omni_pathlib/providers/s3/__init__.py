

from omni_pathlib.path_like import BasePath


class S3Path(BasePath): 

    @property
    def protocol(self) -> str:
        return 's3'

    def __init__(self, path: str):
        super().__init__(path)