from pathlib import Path


class File:
    def __init__(self, file_name: str, dir_path: Path, owner):
        self.owner = owner  # ссылка на Storage, в котором находится этот файл
        self.file_path = dir_path / file_name
        self.file_name = file_name
        self.user_extension = file_name.split('.')[-1]

        self.tree_file_instance = None  # Ссылка на Tree.File
        self.id = None  # self.tree_file_instance._id

        self.filetype = None
        self.filetype_extension = None
        self.file_is = None

    def set_attributes(self, **attributes):
        for attr, value in attributes:
            self.__setattr__(attr, value)

    def get_buttons(self) -> list[str]:
        return self.tree_file_instance.buttons

    def exists(self) -> bool:
        return self.file_path.exists()

    def __repr__(self):
        return f"<name={self.file_name} id={self.tree_file_instance.id} path={self.file_path.resolve()} file_type=" \
               f"{self.file_is}>"
