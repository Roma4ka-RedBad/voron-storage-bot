from logic_objects.file import FileObject


class Base:
    def __init__(self, file: FileObject, process_dir: str, result_dir: str):
        self.file = file
        self.process_dir = process_dir
        self.result_dir = result_dir

    def get_new_filename(self, to_format: str):
        return f"{self.result_dir}/{self.file.get_destination(only_name=True).split('.')[0]}" \
               f".{to_format}"
