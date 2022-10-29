import os
from aiogram.types.message import Message
from misc.models.server import Server

from zipfile import is_zipfile
from rarfile import is_rarfile


class DownloadedFile:
    def __init__(self, main_dir, user_dir, file_name):
        self.main_dir = main_dir
        self.user_dir = user_dir
        self.name = file_name
        self.archive_files = []

    def get_dir(self, with_name=True):
        return f"{self.main_dir}/{self.user_dir}/{self.name if with_name else ''}"

    def is_archive(self):
        return is_zipfile(self.get_dir()) or is_rarfile(self.get_dir())

    async def get_converts(self, server: Server):
        converts = await server.send_msg('converts', [{
            'path': self.get_dir()
        }])
        if self.is_archive():
            for archive_file in converts.content.converts.archive_files:
                self.archive_files.append(archive_file.name)

        return converts.content

    def get_index_by_archive_filename(self, archive_filename: str):
        return self.archive_files.index(archive_filename)

    @classmethod
    async def get_file_by_reply_message(cls, message: Message, server_config, server: Server):
        main_dir = f"{server_config.UFS.path}{server.messenger}"
        user_dir = f"{message.from_user.id}/{message.message_id}"

        if os.path.exists(f"{main_dir}/{user_dir}/{message.document.file_name}"):
            return DownloadedFile(main_dir, user_dir, message.document.file_name)
