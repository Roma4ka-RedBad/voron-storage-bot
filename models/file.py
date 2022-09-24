from pydantic import BaseModel


class FileObject(BaseModel):
    name: str
    size: int = 0
    format: str = None
    tg_hash: str = None

    def size_to_mb(self):
        return self.size / 1024 / 1024

    def size_to_gb(self):
        return self.size / 1024 / 1024 / 1024