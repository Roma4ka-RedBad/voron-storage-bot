from pathlib import Path

from box import Box
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

from misc.models import ConfigModel


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
    bot_api: API = None
    user_api: API = None
    server = None
    labelers: Labelers = Labelers
    state_dispenser: BuiltinStateDispenser = None
    server_config: ConfigModel = None
    default_path: Path = None
    localizations: dict | Box = None

    @classmethod
    async def init(cls, server, *_):
        cls._ = _
        cls.server = server
        await cls.server.connect()
        await cls.update_config_data()

        cls.user_api = API(cls.server_config.VK.user_token)
        cls.bot_api = API(cls.server_config.VK.bot_token)
        cls.state_dispenser = BuiltinStateDispenser()
        cls.default_path = Path(f'{cls.server_config.UFS.path}VK/').absolute()

    @classmethod
    async def update_config_data(cls):
        server_config = await cls.server.get_config()
        cls.server_config = ConfigModel.validate(server_config.config)
        cls.localizations = Box(server_config.localization)

    @classmethod
    def __all__(cls):
        return [
            cls.server,
            cls.server_config,
            cls.bot_api,
            cls.user_api,
            cls.labelers,
            cls.state_dispenser,
            cls.default_path
        ]
