import shutil
from typing import Union, Literal
from zipfile import is_zipfile

from py7zr import is_7zfile
from rarfile import is_rarfile

from misc.utils import super_ as super
from .gzip import GzipArchive
from .rar import RarArchive
from .zip import ZipArchive

"""
Если нужно использовать обычный super:
import builtins
builtins.super()
"""


class Archive(ZipArchive, RarArchive, GzipArchive):
    def __init__(self, file_object, archive_type: Literal['zip', 'rar', '7z']):
        self.user_message_id = file_object.user_message_id
        self.bot_message_ids = []
        self.chat_id = file_object.chat_id
        self.platform_name = file_object.platform_name

        path = file_object.file_path

        if archive_type == 'zip':
            super(ZipArchive).__init__(path)
        elif archive_type == 'rar':
            super(RarArchive).__init__(path)
        elif archive_type == '7z':
            super(GzipArchive).__init__(path)

    async def object_deleter(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)

    @staticmethod
    def is_archive(file_object) -> Union["Archive", bool]:
        if is_zipfile(file_object.file_path):
            return Archive(file_object, 'zip')

        elif is_7zfile(file_object.file_path):
            return Archive(file_object, '7z')

        elif is_rarfile(file_object.file_path):
            return Archive(file_object, 'rar')

        return False

    def __repr__(self):
        return f"<Path={self.file_path.resolve()}>"
