import shutil
from pathlib import Path
from typing import Union
from zipfile import ZipFile

from py7zr import SevenZipFile
from rarfile import RarFile

from .file import BaseArchiveFile


class BaseArchive:
    def __init__(self, path: Path, archive_obj: Union[ZipFile, RarFile, SevenZipFile]):
        self.archive_obj = archive_obj

        self.dir_path = Path(path.parent)
        self.file_name = path.name
        self.file_path = path

        self.files = None
        self._owner_id = None

    def get_files(self):
        if self.files:
            return self.files

        new_files_list = []
        for _id, file in enumerate(self.archive_obj.infolist()):
            if not file.is_dir():
                new_files_list.append(BaseArchiveFile(file, self))
        self.files = new_files_list

        return new_files_list

    def count(self):
        return len(self.archive_obj.namelist())

    def write(self, filepath, arc_name=None):
        if arc_name is None:
            arc_name = Path(filepath).name
        self.archive_obj.write(filepath, arcname=arc_name)

    def close(self):
        self.archive_obj.close()
        return self.file_path

    def get_file(self, instance: Union[int, str]):
        if isinstance(instance, int):
            for file in self.files:
                if file.file_id == instance:
                    return file
        elif isinstance(instance, str):
            for file in self.files:
                if file.origin.filename == instance:
                    return file

        return None

    def create_path(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def get_available_converts(self):
        pass

    async def object_deleter(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)

    def __len__(self):
        return self.count()

    def __repr__(self):
        return f"<Archive id={self.id} path={self.file_path.resolve()}>"
