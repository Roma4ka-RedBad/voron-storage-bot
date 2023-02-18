from typing import Union, BinaryIO
from zipfile import ZipInfo

from py7zr import py7zr
from rarfile import RarInfo

from misc.utils import BytesIO, IO


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
        self.filetype = None
        self.filetype_extension = None
        self.file_is = None

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

    def set_attributes(self, **attributes):
        for attr, value in attributes:
            self.__setattr__(attr, value)

    def get_buttons(self):
        return self.tree_file_instance.buttons

    def __repr__(self):
        return str({
            'name': self.origin.filename,
            'type': self.file_is
        })

    def __str__(self):
        return f'name: {self.origin.filename} type: {self.file_is}'
