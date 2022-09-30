import os
import zipfile
from pydantic import BaseModel


class FileObject(BaseModel):
    name: str
    messenger: str

    def set_config(self, config):
        FileObject.config = config

    def is_exist(self):
        return os.path.exists(self.get_destionation())

    def get_destionation(self):
        return f'{self.config.box.UFS.path}{self.messenger}/{self.name}'

    def get_format(self):
        return self.name.split('.')[-1]

    def is_archive(self):
        return zipfile.is_zipfile(self.get_destionation())


class ArchiveFile:
    def __init__(self, zip_file: zipfile.ZipInfo):
        self.origin = zip_file

    def get_format(self):
        return self.origin.filename.split('.')[-1]

    def get_shortname(self):
        return self.origin.filename.split('/')[-1]

    def is_dir(self):
        return self.origin.is_dir()

    def size_to_mb(self):
        return self.origin.file_size / 1024 / 1024

    def size_to_gb(self):
        return self.origin.file_size / 1024 / 1024 / 1024


class ArchiveObject:
    def __init__(self, file: FileObject, mode):
        self.file = zipfile.ZipFile(file.get_destionation(), mode)

    def get_files(self):
        new_files_list = []
        for file in self.file.infolist():
            new_files_list.append(ArchiveFile(file))
        return new_files_list

    def count(self):
        return len(self.file.infolist())
