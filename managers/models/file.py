import shutil
from pathlib import Path

from logic_objects.config import Config
from misc.utils import guess_file_format


class File:
    def __init__(self, file_name: str, user_message_id: int, chat_id: int, platform_name: str):
        self.user_message_id = user_message_id
        self.bot_message_ids = []
        self.chat_id = chat_id
        self.platform_name = platform_name

        self.dir_path = Path(f"{Config.UFS.path}/{self.platform_name}/{self.chat_id}/{self.user_message_id}")
        self.file_path = self.dir_path / file_name
        self.file_name = file_name
        self.user_extension = file_name.split('.')[-1]

        self.tree_file_instance = None

        self.filetype, self.filetype_extension, self.file_is = guess_file_format(
                Path(self.file_name), open(self.file_path, 'rb'))

    def create_path(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    async def object_deleter(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)

    def __repr__(self):
        return f"< path={self.file_path.resolve()}>"
