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

    def get_dir(self, full=False, with_name=True):
        return f"{self.main_dir + '/' if full else ''}{self.user_dir}/{self.name if with_name else ''}"

    def get_index(self):
        files = os.listdir(self.get_dir(full=True, with_name=False))
        for file in files:
            if file == self.name:
                return files.index(file)

    def is_archive(self):
        return is_zipfile(self.get_dir(full=True)) or is_rarfile(self.get_dir(full=True))

    @classmethod
    async def get_file_by_reply_message(cls, message: Message, server_config, server: Server):
        main_dir = f"{server_config.UFS.path}{server.messenger}"
        user_dir = f"{message.from_user.id}/{message.message_id}"

        if os.path.exists(f"{main_dir}/{user_dir}/{message.document.file_name}"):
            return DownloadedFile(main_dir, user_dir, message.document.file_name)
