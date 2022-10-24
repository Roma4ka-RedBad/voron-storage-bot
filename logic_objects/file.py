import os

from zipfile import ZipFile, ZipInfo, is_zipfile
from rarfile import RarFile, RarInfo, is_rarfile

from pydantic import BaseModel
from box import Box
from copy import copy


class FileObject(BaseModel):
    path: str
    messenger: str
    archive_file: str = None
    config: Box = None

    def set_config(self, config):
        self.config = config

    def is_exist(self):
        return os.path.exists(self.get_destination())

    @classmethod
    def create(cls, filepath, messenger, config):
        open(filepath, 'w').close()
        filepath = filepath.replace(f'{config.UFS.path}{messenger}', '')
        return FileObject(path=filepath, messenger=messenger, config=config)

    def get_destination(self, only_dir=False, only_name=False):
        name = self.path.replace('\\', '/').split('/')[-1]
        if only_dir:
            return f"{self.config.UFS.path}{self.messenger}/{self.path.replace(name, '')}"

        if only_name:
            return name

        return f"{self.config.UFS.path}{self.messenger}/{self.path}"

    def get_format(self):
        return self.path.split('.')[-1]

    def get_available_converts(self):
        converts = [copy(self.config.CONVERTS[group]) for group in self.config.CONVERTS if
                    self.get_format() in self.config.CONVERTS[group]]
        if converts:
            converts = converts[0]
            converts.remove(self.get_format())

        return converts

    def get_archive(self):
        archive_type = None
        if is_zipfile(self.get_destination()):
            archive_type = 'zip'
        elif is_rarfile(self.get_destination()):
            archive_type = 'rar'

        if archive_type:
            return ArchiveObject(self, 'r', archive_type)


class ArchiveFile:
    def __init__(self, zip_file: ZipInfo | RarInfo, archive_file: FileObject,
                 archive_object: ZipFile | RarFile):
        self.origin = zip_file
        self.archive_file = archive_file
        self.archive_object = archive_object

    def get_format(self):
        return self.origin.filename.split('.')[-1]

    def get_shortname(self):
        return self.origin.filename.split('/')[-1]

    def is_dir(self):
        return self.origin.is_dir()

    def size_to_mb(self):
        return self.origin.file_size / 1024 / 1024

    def extract(self, path):
        return self.archive_object.extract(self.origin, path)

    def get_available_converts(self):
        converts = [copy(self.archive_file.config.CONVERTS[group]) for group in self.archive_file.config.CONVERTS if
                    self.get_format() in self.archive_file.config.CONVERTS[group]]
        if converts:
            converts = converts[0]
            converts.remove(self.get_format())

        return converts


class ArchiveObject:
    def __init__(self, file: FileObject, mode, archive_type: str):
        self.file = file
        if archive_type == 'zip':
            self.archive = ZipFile(file.get_destionation(), mode)
        elif archive_type == 'rar':
            self.archive = RarFile(file.get_destionation(), mode)

    def get_file_by_name(self, name):
        for file in self.get_files():
            if file.get_shortname() == name:
                return file

    def get_files(self):
        new_files_list = []
        for file in self.archive.infolist():
            new_files_list.append(ArchiveFile(file, self.file, self.archive))
        return new_files_list

    def get_available_converts(self):
        result = []
        for file in self.get_files():
            result = list(set(result + file.get_available_converts()))
        return result

    def count(self):
        return len(self.archive.infolist())

    def write(self, filepath):
        self.archive.write(filepath, arcname=filepath.split('/')[-1])
