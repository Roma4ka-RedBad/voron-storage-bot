from rarfile import RarFile

from ..base import BaseArchive


class RarArchive(BaseArchive):
    def __init__(self, path, **kwargs):
        archive = RarFile(path, **kwargs)
        super().__init__(path, archive)
