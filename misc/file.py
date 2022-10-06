import os
from aiogram.types.message import Message
from misc.server import Server
from zipfile import is_zipfile


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
        return is_zipfile(self.get_dir(full=True))

    @classmethod
    async def get_file_by_index_or_name(cls, message: Message, server: Server, file_index: int = None,
                                        file_name: str = None):
        config = await server.send_message('config')
        main_dir = f"{config.content.UFS.path}{server.messenger}"
        user_dir = f"{message.from_user.id}/{message.message_id}"

        if os.path.exists(f"{main_dir}/{user_dir}"):
            files = os.listdir(f"{main_dir}/{user_dir}")
            for index, file in enumerate(files):
                if file_index is not None:
                    if index == file_index:
                        return DownloadedFile(main_dir, user_dir, file)

                if file_name:
                    if file == file_name:
                        return DownloadedFile(main_dir, user_dir, file)
