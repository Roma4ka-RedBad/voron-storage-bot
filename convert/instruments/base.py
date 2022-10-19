from logic_objects.file import FileObject


class Base:
    def __init__(self, file: FileObject):
        self.file = file

    def get_new_filename(self, to_format: str):
        return f"new_files/{self.file.get_destionation(only_shortname=True).split('.')[0]}.{to_format}"