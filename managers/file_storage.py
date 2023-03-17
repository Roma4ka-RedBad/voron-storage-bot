import shutil
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from pytz import timezone

from logic_objects.config import Config
from managers.connections import ConnectionsManager
from managers.models import SearchingQuery, Archive, File
from misc.converts import Tree, Converts
from misc.utils import guess_file_format
from packets.base import Packet


class Storage:
    # Перенесешь куда-нибудь. Эта штука будет отвечать за конверты.
    def __init__(self, obj_id: int, user_message_id: int, chat_id: int, platform_name: str):
        self.user_message_id = user_message_id
        self.chat_id = chat_id
        self.platform_name = platform_name
        self.bot_message_ids = []
        self.dir_path = Path(f"{Config.UFS.path}/{self.platform_name}/{self.chat_id}/{self.user_message_id}")
        self.object_id = obj_id

        self.tree = None  # обновляется в функции self.register_files
        self.raw_objects: list[File] = []
        self.file_objects = []

        self.total_size = 0
        self.total_files_count = 0
        self.last_size = 0
        self.last_raw_files_count = 0

        self.id = None
        self.converts = None
        self.create_path()

    def add_raw_files(self, *files):
        self.last_size = sum(file['file_size'] for file in files)
        self.last_raw_files_count = len(files)
        for file in files:
            self.raw_objects.append(File(file['name'], self.dir_path, self))

    def rollback(self) -> int:
        last_size = self.last_size
        self.total_size -= self.last_size
        self.last_size = 0
        self.raw_objects = self.raw_objects[:-self.last_raw_files_count]
        self.last_raw_files_count = 0

        return last_size

    def add(self, file: File | Archive):
        if isinstance(file, File):
            self.file_objects.append(file)
            temp = guess_file_format(Path(file.file_name), open(file.file_path, 'rb'))
            file.set_attributes(filetype=temp[0], filetype_extension=temp[1], file_is=temp[2])
            file.tree_file_instance = self.tree.add(file)

        elif isinstance(file, Archive):
            for archive_file in file.get_files():
                self.file_objects.append(archive_file)
                temp = guess_file_format(Path(archive_file.file_name), open(file.file_path, 'rb'))
                archive_file.set_attributes(filetype=temp[0], filetype_extension=temp[1], file_is=temp[2])
                archive_file.tree_file_instance = self.tree.add(archive_file)

    def get_files_count(self) -> int:
        files_count = 0
        for file_object in self.raw_objects:
            if not file_object.exists():
                if file := Archive.is_archive(file_object):
                    files_count += len(file)
                else:
                    files_count += 1

        self.total_files_count = files_count
        return files_count

    def register_files(self):
        self.tree = Tree()
        self.file_objects.clear()
        for file_object in self.raw_objects:
            if file_object.exists():
                self.add(Archive.is_archive(file_object, return_file_object=True))

    def get_available_converts(self, *converts: Converts | None) -> dict:
        """
        :param converts: Список конкретных конвертаций, на которые нужно сделать проверку.
        :return: Словарь кнопок и массив ид файлов, которые подходят под категорию конвертации. Может быть пустым.
        {'button': {'file_ids': [int | tuple[int]], 'warnings': [str]}, ...}
        """
        if not converts:
            converts = Converts.__all__()
        self.converts = Converts.match_available_converts(self.tree.files.values(), *converts)

        return self.converts

    async def convert_to(self, method: str):
        if self.converts is None:
            self.get_available_converts()

        if method not in self.converts:
            return {'error_tid': 'WORK_FILE_NOT_CONVERT_ERROR'}
        #  Ну и по идее, тут файлы добавляются в очередь и ждётся ответ.
        #  Возвращается список путей на конвертированные файлы
        return {'paths': [str(obj.file_path.resolve()) for obj in self.file_objects]}

    def create_path(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)

    async def object_deleter(self):
        shutil.rmtree(self.dir_path, ignore_errors=True)


class FileManager:
    def __init__(self, connection_manager: ConnectionsManager):
        self.objects = []
        self.scheduler = AsyncIOScheduler()
        self.cm = connection_manager

        self._unique_id = 0

    async def register(self, object_type: str, **kwargs) -> SearchingQuery | Storage:
        _object = None
        if object_type == 'query':
            _object = SearchingQuery(obj_id=self._get_unique_id(), **kwargs)
        elif object_type == 'file':
            _object = Storage(obj_id=self._get_unique_id(), **kwargs)

        if _object:
            _object.id = self._get_unique_id()
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

    async def remove(self, object_id: int = None, _object: Storage | SearchingQuery = None,
                     forcibly_remove_job: bool = False,
                     remove_messages: bool = True):
        for __object in self.objects:
            if __object.object_id == object_id or __object == _object:
                await __object.object_deleter()
                if forcibly_remove_job:
                    self.scheduler.get_job(str(__object.object_id)).remove()
                if remove_messages:
                    await self.cm.send_by_handlers(
                            Packet(20102, platform_name=__object.platform_name,
                                   message_ids=[__object.user_message_id] + __object.bot_message_ids,
                                   chat_id=__object.chat_id))
                self.objects.remove(__object)

    async def get(self, object_id: int) -> SearchingQuery | Storage:
        for _object in self.objects:
            if _object.object_id == object_id:
                return _object

    async def reload_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.reschedule(DateTrigger(
                    datetime.now(tz=timezone(Config.SERVER.timezone)) + timedelta(
                            minutes=Config.UFS.wait_for_delete_dir),
                    timezone=timezone(Config.SERVER.timezone)
            )).resume()

    async def stop_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.pause()

    async def resume_task(self, object_id: int):
        if object_task := self.scheduler.get_job(str(object_id)):
            object_task.resume()

    def _get_unique_id(self) -> int:
        self._unique_id += 1
        # яхз может вообще по приколу бесконечным сделать? Я просто думал, что в пакете есть ограничение на размер
        # этого значения
        if self._unique_id > 1_000_000:
            self._unique_id = 0

        return self._unique_id
