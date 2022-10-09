import os
import zipfile

from pydantic import BaseModel
from box import Box
from copy import copy


class FileObject(BaseModel):
    name: str
    messenger: str
    config: Box = None

    def set_config(self, config):
        self.config = config

    def is_exist(self):
        return os.path.exists(self.get_destionation())

    def get_destionation(self, only_dir=False, only_shortname=False):
        shortname = self.name.split('/')[-1]
        if only_dir:
            return f"{self.config.UFS.path}{self.messenger}/{self.name.replace(shortname, '')}"

        if only_shortname:
            return shortname

        return f"{self.config.UFS.path}{self.messenger}/{self.name}"

    def get_format(self):
        return self.name.split('.')[-1]

    def get_available_converts(self):
        converts = [copy(self.config.CONVERTS[group]) for group in self.config.CONVERTS if
                    self.get_format() in self.config.CONVERTS[group]]
        if converts:
            converts = converts[0]
            converts.remove(self.get_format())

        return converts

    def get_archive(self):
        if zipfile.is_zipfile(self.get_destionation()):
            return ArchiveObject(self, 'r')


class ArchiveFile:
    def __init__(self, zip_file: zipfile.ZipInfo, archive_file: FileObject):
        self.origin = zip_file
        self.archive_file = archive_file

    def get_format(self):
        return self.origin.filename.split('.')[-1]

    def get_shortname(self):
        return self.origin.filename.split('/')[-1]

    def is_dir(self):
        return self.origin.is_dir()

    def size_to_mb(self):
        return self.origin.file_size / 1024 / 1024

    def get_available_converts(self):
        converts = [copy(self.archive_file.config.CONVERTS[group]) for group in self.archive_file.config.CONVERTS if
                    self.get_format() in self.archive_file.config.CONVERTS[group]]
        if converts:
            converts = converts[0]
            converts.remove(self.get_format())

        return converts


class ArchiveObject:
    def __init__(self, file: FileObject, mode):
        self.file = file
        self.archive = zipfile.ZipFile(file.get_destionation(), mode)

    def get_files(self):
        new_files_list = []
        for file in self.archive.infolist():
            new_files_list.append(ArchiveFile(file, self.file))
        return new_files_list

    def get_available_converts(self):
        result = []
        for file in self.get_files():
            result = list(set(result + file.get_available_converts()))
        return result

    def count(self):
        return len(self.archive.infolist())
