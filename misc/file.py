import os
from zipfile import is_zipfile


class DownloadedFile:
    def __init__(self, main_dir, user_dir, file_name):
        self.main_dir = main_dir
        self.user_dir = user_dir
        self.name = file_name

    def get_dir(self, full=False, with_name=True):
        return f"{self.main_dir + '/' if full else ''}{self.user_dir}/{self.name if with_name else ''}"

    def get_index(self):
        files = os.listdir(self.get_dir(full=True, with_name=False))
        for file in files:
            if file == self.name:
                return files.index(file)

    def is_archive(self):
        return is_zipfile(self.get_dir(full=True))
