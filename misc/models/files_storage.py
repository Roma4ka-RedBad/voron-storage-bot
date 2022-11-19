from .file import DFile, IFile
from datetime import datetime


class FilesStorage:
    def __init__(self):
        self.storage = {}
        self.active_converts = []

    async def put(self, file: DFile | IFile):
        last_id = 0
        if len(list(self.storage)) > 0:
            last_id = list(self.storage)[-1] + 1

        self.storage.update({last_id: file} )
        return last_id

    async def put_convert(self, file_id: int):
        key_id = f"{file_id}_{datetime.now()}"
        self.active_converts.append(key_id)
        return key_id

    async def get(self, key_id: int) -> DFile | IFile:
        try:
            return self.storage[key_id]
        except:
            pass

    async def get_convert(self, file_id: int):
        for key_id in self.active_converts:
            if str(file_id) in key_id:
                return True

    async def delete(self, key_id: int):
        self.storage.pop(key_id)

    async def delete_convert(self, key_id: str):
        self.active_converts.remove(key_id)

    async def convert_worked(self, file_id: int):
        for key_id in self.active_converts:
            if str(file_id) in key_id:
                return True
