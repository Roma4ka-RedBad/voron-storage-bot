from logic_objects.file import FileObject


class Base:
    def __init__(self, file: FileObject, result_dir: str):
        self.file = file
        self.result_dir = result_dir

    def get_new_filename(self, to_format: str):
        return f"{self.result_dir}/{self.file.path.stem}.{to_format}"
