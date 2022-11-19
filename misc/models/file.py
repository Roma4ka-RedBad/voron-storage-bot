import os
from pathlib import Path
from aiogram.types.message import Message
from misc.models.server import Server

from zipfile import is_zipfile
from rarfile import is_rarfile


class DFile:
    def __init__(self, path, message: Message):
        self.path = Path(path)
        self.message = message
        self.bot_answer = None
        self.target_files = []
        self.converts = None

    def is_archive(self):
        return is_zipfile(self.path) or is_rarfile(self.path)

    async def get_converts(self, server: Server):
        self.converts = await server.send_msg('converts', [{
            'path': str(self.path)
        }])
        if self.is_archive():
            if self.converts.status:
                for archive_file in self.converts.content[0].converts.archive_files:
                    self.target_files.append(archive_file.name)

    def get_index_by_target_filename(self, archive_filename: str):
        return self.target_files.index(archive_filename)

    def get_target_filename_by_index(self, index: int):
        if index is not None:
            return self.target_files[index]


class IFile:
    def __init__(self, path, message: Message, server_response):
        self.path = Path(path)
        self.message = message
        self.server_response = server_response

    async def get_text_file(self):
        os.makedirs(self.path.absolute(), exist_ok=True)
        file_path = (self.path / f'files_{self.server_response.version}.txt').absolute()
        with open(file_path, 'w') as file:
            file.write('\n'.join(self.server_response.files))
            file.close()
        return file_path

    async def download(self, server: Server):
        os.makedirs(self.path.absolute(), exist_ok=True)
        version = self.server_response.version.split('.')
        file = await server.send_msg('download_files', game_data={
            'path': str(self.path),
            'search_query': '|'.join(self.server_response.files),
            'major_v': version[0],
            'build_v': version[1],
            'revision_v': version[2]
        }, metadata={'compress_to_archive': True if len(self.server_response.files) > 1 else False})
        if file:
            if file.status:
                return file.content if len(self.server_response.files) > 1 else file.content[0]
