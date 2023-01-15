import random
import shutil
from pathlib import Path
from logic_objects.config import Config


class File:
    def __init__(self, file_name: str, user_message_id: int, chat_id: int, platform_name: str):
        self.user_message_id = user_message_id
        self.bot_message_ids = []
        self.chat_id = chat_id
        self.platform_name = platform_name

        self.object_id = random.randint(0, 10000000)
        self.dir_path = Path(f"{Config.UFS.path}/{self.platform_name}/{self.chat_id}/{self.user_message_id}")
        self.file_path = self.dir_path / file_name

    def __repr__(self):
        return f"<File id={self.object_id} path={self.file_path.resolve()}>"

    def create_path(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def get_available_converts(self):
        converts = Config.get_converts()
        return converts.get(self.file_path.suffix[1:], None)

    async def object_deleter(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)
