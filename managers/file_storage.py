from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from pytz import timezone

from managers.connections import ConnectionsManager
from managers.manager_models import SearchingQuery, File
from logic_objects.config import Config
from packets.base import Packet


class FileManager:
    def __init__(self, connection_manager: ConnectionsManager):
        self.objects = []
        self.scheduler = AsyncIOScheduler()
        self.cm = connection_manager

    async def register(self, object_type: str, **kwargs) -> SearchingQuery | File:
        _object = None
        if object_type == 'query':
            _object = SearchingQuery(**kwargs)
        elif object_type == 'file':
            _object = File(**kwargs)

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
                await self.cm.send_by_handlers(
                    Packet(20102, platform_name=__object.platform_name,
                           message_ids=[__object.user_message_id] + __object.bot_message_ids,
                           chat_id=__object.chat_id))
                self.objects.remove(__object)

    async def get(self, object_id: int) -> SearchingQuery | File:
        for _object in self.objects:
            if _object.object_id == object_id:
                return _object

    async def reload_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.reschedule(DateTrigger(
                datetime.now(tz=timezone(Config.SERVER.timezone)) + timedelta(minutes=Config.UFS.wait_for_delete_dir),
                timezone=timezone(Config.SERVER.timezone)
            )).resume()

    async def stop_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.pause()

    async def resume_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.resume()
