from .file import DownloadedFile


class FilesStorage:
    def __init__(self):
        self.storage = {}

    def put(self, file: DownloadedFile):
        last_id = list(self.storage)[-1] + 1
        self.storage.update({last_id: file})
        return last_id

    def get(self, key_id: int):
        if key_id in self.storage:
            return self.storage[key_id]

    def delete(self, key_id):
        self.storage.pop(key_id)
