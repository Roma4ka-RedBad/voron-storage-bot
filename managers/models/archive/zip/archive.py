from pathlib import Path
from typing import Union, Literal
from zipfile import ZipFile

from ..base import BaseArchive


class ZipArchive(BaseArchive):
    def __init__(self, path, **kwargs):
        archive = ZipFile(path, **kwargs)
        super().__init__(path, archive)
        print('is zip')

    @staticmethod
    def create_empty(path: Union[Path, str], mode: Literal["w", "x", "a"] = 'w', compress_level: int = 10, **kwargs):
        if isinstance(path, str):
            path = Path(path)
        path = path.absolute().resolve()
        path.parent.mkdir(exist_ok=True, parents=True)

        return ZipArchive(path, mode=mode, compresslevel=compress_level, **kwargs)
