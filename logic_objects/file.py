import shutil, os

from pathlib import Path
from zipfile import ZipFile, ZipInfo, is_zipfile
from rarfile import RarFile, RarInfo, is_rarfile

from pydantic import BaseModel
from box import Box
from copy import copy


class FileObject(BaseModel):
    path: Path
    target_file: str = None
    config: Box = None

    def set_config(self, config):
        self.config = config

    def copy_to(self, filepath):
        if self.path.parent != Path(filepath):
            filepath = shutil.copy(str(self.path), str(filepath))
        else:
            filepath = self.path

        return FileObject(path=filepath, config=self.config)

    @classmethod
    def create(cls, filepath, config):
        open(filepath, 'w').close()
        return FileObject(path=filepath, config=config)

    def get_available_converts(self):
        converts = [copy(self.config.CONVERTS[group]) for group in self.config.CONVERTS if
                    self.path.suffix[1:] in self.config.CONVERTS[group]]
        if converts:
            converts = converts[0]
            converts.remove(self.path.suffix[1:])

        return converts

    def get_archive(self):
        archive_type = None
        if is_zipfile(self.path):
            archive_type = 'zip'
        elif is_rarfile(self.path):
            archive_type = 'rar'

        if archive_type:
            return ArchiveObject(self, 'r', archive_type)


class ArchiveFile:
    def __init__(self, archive_file: ZipInfo | RarInfo, archive_file_object: FileObject,
                 archive_object: ZipFile | RarFile):
        self.origin = archive_file
        self.archive_file = archive_file_object
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
        return FileObject(path=self.archive_object.extract(self.origin, path), config=self.archive_file.config)

    def get_available_converts(self):
        converts = [copy(self.archive_file.config.CONVERTS[group]) for group in self.archive_file.config.CONVERTS if
                    self.get_format() in self.archive_file.config.CONVERTS[group]]
        if converts:
            converts = converts[0]
            converts.remove(self.get_format())

        return converts


class ArchiveObject:
    def __init__(self, file: FileObject, mode, archive_type: str, **kwargs):
        self.file = file
        if archive_type == 'zip':
            self.archive = ZipFile(file.path, mode, **kwargs)
        elif archive_type == 'rar':
            self.archive = RarFile(file.path, mode, **kwargs)

    def get_file_by_name(self, name):
        for file in self.get_files():
            if file.origin.filename == name:
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

    def write(self, filepath, arc_name=None):
        if arc_name is None:
            arc_name=filepath.name
        self.archive.write(filepath, arcname=arc_name)

    def close(self):
        self.archive.close()
        return self.file.path