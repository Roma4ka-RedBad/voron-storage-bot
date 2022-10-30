from .file import DownloadedFile


class FilesStorage:
    def __init__(self):
        self.storage = {}

    async def put(self, file: DownloadedFile):
        last_id = 0
        if len(list(self.storage)) > 0:
            last_id = list(self.storage)[-1] + 1

        self.storage.update({last_id: file} )
        return last_id

    async def get(self, key_id: int) -> DownloadedFile:
        if key_id in self.storage:
            return self.storage[key_id]

    async def delete(self, key_id):
        self.storage.pop(key_id)
