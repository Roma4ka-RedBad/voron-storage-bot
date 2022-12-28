import asyncio
from pathlib import Path
from typing import Coroutine, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

from misc.models.server import Server


class Labelers:
    labelers = []

    @classmethod
    def new(cls) -> BotLabeler:
        labeler = BotLabeler()
        cls.labelers.append(labeler)
        return labeler

    @classmethod
    def __all__(cls):
        return cls.labelers

    @classmethod
    def __repr__(cls):
        return str(cls.labelers)


class Config:
    api: API = None
    server: Server = None
    labelers: Labelers = Labelers
    state_dispenser: BuiltinStateDispenser = None
    server_config = None
    scheduler: AsyncIOScheduler = None
    default_path: Path = None

    @classmethod
    def __init__(cls):
        cls.scheduler = AsyncIOScheduler()
        cls.server = Server('http://127.0.0.1:8910')
        cls.server_config = (cls._run_coro(cls.server.send_message('config'))).content
        cls.server.timezone = timezone(cls.server_config.SERVER.timezone)
        cls.api = API(cls.server_config.VK.bot_token)
        cls.state_dispenser = BuiltinStateDispenser()
        cls.default_path = Path(f'{cls.server_config.UFS.path}VK/').absolute()

    @classmethod
    def __all__(cls):
        return [
            cls.scheduler,
            cls.server,
            cls.server_config,
            cls.server.timezone,
            cls.api,
            cls.labelers,
            cls.state_dispenser,
            cls.default_path
        ]

    @staticmethod
    def _run_coro(coro: Coroutine) -> Any:
        return asyncio.run(coro)


bot_config = Config()
