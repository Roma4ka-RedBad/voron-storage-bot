from py7zr import SevenZipFile

from .file import GzipArchiveFile
from ..base import BaseArchive


class GzipArchive(BaseArchive):
    def __init__(self, path, **kwargs):
        archive = SevenZipFile(path, **kwargs)
        super().__init__(path, archive)

    def get_files(self) -> list[GzipArchiveFile]:
        if self.files:
            return self.files

        new_files_list = []
        files = {file.filename: file for file in self.archive_obj.files}

        for filename, io in self.archive_obj.readall().items():
            new_files_list.append(GzipArchiveFile(files[filename], self, io))

        self.files = new_files_list
        return new_files_list

    def count(self) -> int:
        return len([file for file in self.archive_obj.files if not file.is_directory])
