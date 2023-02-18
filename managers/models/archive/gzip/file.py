from typing import IO, BinaryIO

from py7zr import py7zr

from ..base import BaseArchiveFile


class GzipArchiveFile(BaseArchiveFile):
    def __init__(self, archive_file: py7zr.ArchiveFile,
                 archive_file_object,
                 bytes_io: BinaryIO | IO):
        super().__init__(archive_file, archive_file_object, bytes_io)

    def is_dir(self):
        return self.origin.is_directory

    def size_to_mb(self):
        return self.origin.uncompressed / 1024 / 1024  # на самом деле тут int отдается

    def extract(self, path):
        self.owner.extract(path, self.origin.filename)
