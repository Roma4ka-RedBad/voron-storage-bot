from logic_objects.file import FileObject
from pathlib import Path


class Base:
    def __init__(self, file: FileObject, result_dir: str):
        self.file = file
        self.result_dir = result_dir

    def get_new_filename(self, to_format: str):
        return Path(f"{self.result_dir}/{self.file.path.stem}.{to_format}")
