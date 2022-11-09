from logic_objects.file import FileObject
from pathlib import Path


class Base:
    def __init__(self, file: FileObject, result_dir: str):
        self.file = file
        self.result_dir = result_dir

    def get_new_filename(self, to_format: str, postfix: str = '', use_any_dir: str | Path = None):
        if not use_any_dir:
            return Path(f"{self.result_dir}/{self.file.path.stem}{postfix}.{to_format}")
        else:
            return Path(f"{str(use_any_dir)}/{self.file.path.stem}{postfix}.{to_format}")
