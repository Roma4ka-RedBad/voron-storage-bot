import asyncio
import shutil
from pathlib import Path

from logic_objects.config import Config
from misc.utils import file_writer


class SearchingQuery:
    def __init__(self, major_v: int, build_v: int, revision_v: int, text_query: str, user_message_id: int,
                 chat_id: int, platform_name: str, obj_id: int):
        self.major_v = major_v
        self.build_v = build_v
        self.revision_v = revision_v
        self.text_query = text_query

        self.user_message_id = user_message_id
        self.bot_message_ids = []
        self.chat_id = chat_id
        self.platform_name = platform_name

        self.object_id = obj_id
        self.path = Path(f"{Config.UFS.path}/{self.platform_name}/{self.chat_id}/{self.user_message_id}")

    def create_path(self):
        self.path.mkdir(parents=True, exist_ok=True)

    async def create_text_document(self, data) -> str:
        self.create_path()
        return await asyncio.to_thread(file_writer, self.path / "files.txt", data, mode="w")

    async def object_deleter(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def __repr__(self):
        return f"<SearchingQuery id={self.object_id} query={self.text_query}>"
