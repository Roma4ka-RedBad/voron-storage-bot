from .file import DownloadedFile
from datetime import datetime


class FilesStorage:
    def __init__(self):
        self.storage = {}
        self.active_converts = []

    async def put(self, file: DownloadedFile):
        last_id = 0
        if len(list(self.storage)) > 0:
            last_id = list(self.storage)[-1] + 1

        self.storage.update({last_id: file} )
        return last_id

    async def put_convert(self, file_id: int):
        key_id = f"{file_id}_{datetime.now()}"
        self.active_converts.append(key_id)
        return key_id

    async def convert_worked(self, file_id: int):
        for key_id in self.active_converts:
            if str(file_id) in key_id:
                return True

    async def get(self, key_id: int, storage = None) -> DownloadedFile:
        if not storage:
            storage = self.storage

        if key_id in storage:
            return storage[key_id]

    async def delete(self, key_id, storage = None):
        if not storage:
            storage = self.storage

        if isinstance(storage, list):
            storage.remove(key_id)
        else:
            storage.pop(key_id)
