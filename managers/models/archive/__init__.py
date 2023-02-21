import os
import shutil
from pathlib import Path
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

__all__ = ['ZipArchive', 'RarArchive', 'GzipArchive', 'Archive']


class Archive(ZipArchive, RarArchive, GzipArchive):
    archive_types = {
        'zip': ZipArchive,
        'rar': RarArchive,
        '7z': GzipArchive
    }

    def __init__(self, file_object, archive_type: Literal['zip', 'rar', '7z'], **kwargs):
        self.user_message_id = file_object.user_message_id
        self.bot_message_ids = []
        self.chat_id = file_object.chat_id
        self.platform_name = file_object.platform_name

        path = file_object.file_path
        super(self.__class__.archive_types[archive_type]).__init__(path, **kwargs)

    async def object_deleter(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)

    @staticmethod
    def is_archive(file_object, return_file_object: bool = False) -> Union["Archive", bool]:
        if is_zipfile(file_object.file_path):
            return Archive(file_object, 'zip')

        elif is_7zfile(file_object.file_path):
            return Archive(file_object, '7z')

        elif is_rarfile(file_object.file_path):
            return Archive(file_object, 'rar')

        if return_file_object:
            return file_object
        return False

    @staticmethod
    async def compress_to_archive(archive_path: str, file_paths: list = None, close_archive: bool = True,
                                  archive_type: Literal['zip', 'rar', '7z'] = 'zip', **kwargs):
        # Если нужны другие типы архивов, кроме зип - нужно создать функцию create_empty
        archive = Archive.archive_types[archive_type].create_empty(archive_path, **kwargs)
        if file_paths:
            for path in file_paths:
                if path:
                    if os.path.isdir(path):
                        for folder, _, files in os.walk(path):
                            for _file in files:
                                arc_name = os.path.join(folder.replace(path, ''), _file)
                                file_name = os.path.join(folder, _file)
                                if arc_name is None:
                                    arc_name = Path(file_name).name
                                archive.write(filepath=file_name, arc_name=arc_name)
                    else:
                        archive.write(path)

        if close_archive:
            return archive.close()  # возвращает путь до архива
        return archive

    def __repr__(self):
        return f"<Path={self.file_path.resolve()} files_count={len(self)}>"
