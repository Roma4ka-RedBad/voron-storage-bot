from typing import Union, BinaryIO
from zipfile import ZipInfo

from py7zr import py7zr
from rarfile import RarInfo

from misc.utils import BytesIO, IO, guess_file_format


class BaseArchiveFile:
    def __init__(self,
                 archive_file: Union[ZipInfo, RarInfo, py7zr.ArchiveFile],
                 archive_object,
                 bytes_io: BinaryIO | IO = None):
        self.origin = archive_file
        self.owner = archive_object

        self.tree_file_instance = None

        if bytes_io is None:
            self.bytes_io = BytesIO(self.owner.archive_obj.open(self.origin.filename))
        else:
            self.bytes_io = BytesIO(bytes_io)

        self.user_extension = self.origin.filename.split('.')[-1]

        # определяется по заголовку и по совокупности условий
        # рекомендуется использовать file_is
        self.filetype, self.filetype_extension, self.file_is = guess_file_format(self.origin.origin, bytes_io)

    def get_format(self):
        return self.user_extension

    def get_shortname(self):
        return self.origin.filename.split('/')[-1]

    def is_dir(self):
        return self.origin.is_dir()

    def size_to_mb(self):
        return self.origin.file_size / 1024 / 1024

    def extract(self, path):
        return self.owner.archive_obj.extract(self.origin, path)

    def __repr__(self):
        return str({
            'name': self.origin.filename,
            'type': self.file_is
        })

    def __str__(self):
        return f'name: {self.origin.filename} type: {self.file_is}'
