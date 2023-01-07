import random
import asyncio
import shutil
from pathlib import Path
from pytz import timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta

from managers.connections import ConnectionsManager
from logic_objects.config import Config
from misc.utils import file_writer


class SearchingQuery:
    def __init__(self, major_v: int, build_v: int, revision_v: int, text_query: str, bind_message_id: int,
                 bind_chat_id: int, platform_name: str):
        self.major_v = major_v
        self.build_v = build_v
        self.revision_v = revision_v
        self.text_query = text_query

        self.bind_message_id = bind_message_id
        self.bind_chat_id = bind_chat_id
        self.platform_name = platform_name

        self.object_id = random.randint(0, 10000000)
        self.path = Path(f"{Config.UFS.path}/{self.platform_name}/{self.bind_chat_id}/{self.bind_message_id}")

    def __repr__(self):
        return f"<SearchingQuery id={self.object_id} query={self.text_query}>"

    def create_path(self):
        self.path.mkdir(parents=True, exist_ok=True)

    async def create_text_document(self, data):
        self.create_path()
        return await asyncio.to_thread(file_writer, self.path / "files.txt", data, mode="w")

    async def object_deleter(self):
        shutil.rmtree(self.path, ignore_errors=True)


class FileManager:
    def __init__(self, connection_manager: ConnectionsManager):
        self.objects = []
        self.scheduler = AsyncIOScheduler()
        self.cm = connection_manager

    async def register(self, object_type: str, **kwargs) -> SearchingQuery:
        _object = None
        if object_type == 'query':
            _object = SearchingQuery(**kwargs)

        if _object:
            self.objects.append(_object)
            self.scheduler.add_job(
                func=self.remove,
                args=[_object.object_id],
                id=str(_object.object_id),
                trigger=DateTrigger(
                    datetime.now(tz=timezone(Config.SERVER.timezone)) + timedelta(
                        minutes=Config.UFS.wait_for_delete_dir),
                    timezone=timezone(Config.SERVER.timezone)
                ),
                misfire_grace_time=None
            )
            return _object

    async def remove(self, object_id: int = None, _object: object = None, forcibly_remove_job: bool = False):
        for __object in self.objects:
            if __object.object_id == object_id or __object == _object:
                await __object.object_deleter()
                if forcibly_remove_job:
                    self.scheduler.get_job(str(__object.object_id)).remove()
                self.objects.remove(__object)

    async def get(self, object_id: int) -> SearchingQuery:
        for _object in self.objects:
            if _object.object_id == object_id:
                return _object

    async def reload_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.reschedule(DateTrigger(
                datetime.now(tz=timezone(Config.SERVER.timezone)) + timedelta(minutes=Config.UFS.wait_for_delete_dir),
                timezone=timezone(Config.SERVER.timezone)
            ))
            object_task.resume()

    async def stop_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.pause()

    async def resume_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.resume()
