import os
import zipfile
from pydantic import BaseModel


class FileObject(BaseModel):
    name: str
    messenger: str
    size: int = 0
    tg_hash: str = None

    def set_config(self, config):
        FileObject.config = config

    def size_to_mb(self):
        return self.size / 1024 / 1024

    def size_to_gb(self):
        return self.size / 1024 / 1024 / 1024

    def is_exist(self):
        return os.path.exists(self.get_destionation())

    def get_destionation(self):
        return f'{self.config.box.UFS.path}{self.messenger}/{self.name}'

    def get_format(self):
        return self.name.split('.')[-1]

    def is_archive(self):
        return zipfile.is_zipfile(self.get_destionation())


class FilePack:
    def __init__(self, zip_file: zipfile.ZipInfo):
        self.origin = zip_file

    def get_format(self):
        return self.origin.filename.split('.')[-1]

    def size_to_mb(self):
        return self.origin.file_size / 1024 / 1024

    def size_to_gb(self):
        return self.origin.file_size / 1024 / 1024 / 1024


class ZIPObject:
    def __init__(self, file: FileObject, mode: str):
        self.file = zipfile.ZipFile(file.get_destionation(), mode)

    def get_files(self):
        new_files_list = []
        for file in self.file.infolist():
            new_files_list.append(FilePack(file))
        return new_files_list

    def count(self):
        return len(self.file.infolist())
