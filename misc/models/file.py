import os

from pathlib import Path
from aiogram.types.message import Message
from misc.models.server import Server

from zipfile import is_zipfile
from rarfile import is_rarfile


class DownloadedFile:
    def __init__(self, path, message: Message):
        self.path = Path(path)
        self.message = message
        self.target_files = []

    def is_archive(self):
        return is_zipfile(self.path) or is_rarfile(self.path)

    async def get_converts(self, server: Server):
        converts = await server.send_msg('converts', [{
            'path': str(self.path)
        }])
        if self.is_archive():
            if converts.status:
                for archive_file in converts.content.converts.archive_files:
                    self.target_files.append(archive_file.name)
        return converts

    def get_index_by_target_filename(self, archive_filename: str):
        return self.target_files.index(archive_filename)

    def get_target_filename_by_index(self, index: int):
        if index:
            return self.target_files[index]
