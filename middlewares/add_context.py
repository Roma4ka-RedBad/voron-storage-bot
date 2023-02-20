from json import loads

from box import Box
from vkbottle import BaseMiddleware
from vkbottle.bot import Message, Bot

from bot_config import Config
from misc.connections import ServerConnection
from misc.models import UserModel
from packets.base import Packet


class AddArgumentsToMessageEventMiddleware(BaseMiddleware[Message]):
    type = 'message'
    server: ServerConnection
    bot: Bot

    def __init__(self, event: Message, view):
        super().__init__(event, view)

    async def pre(self):
        # Документация говорит обращаться к аттрибутам класса через self.__class__
        userdata = await self.__class__.server.send(Packet(11100, vk_id=self.event.from_id))

        if not userdata.payload:
            if self.event.from_id in Config.server_config.VK.admin_ids:
                await self.event.answer('Подключение к серверу отсутствует')
            else:
                await self.event.answer(
                        'Произошла ошибка подключения к серверу. '
                        'Обратитесь к администраторам '
                        '([id508214061|Сева Чел], [id361332053|Рома Романов])')
            self.stop()

        else:
            payload = Box(loads(self.event.payload)) if self.event.payload else self.event.payload
            userdata = UserModel.validate(userdata.payload)
            self.send(
                    {
                        'server': self.__class__.server,
                        'userdata': userdata,
                        'localization': Config.localizations[userdata.language_code],
                        'payload': payload,
                        'bot': self.__class__.bot,
                    })


class AddArgumentsToCallbackEventMiddleware(BaseMiddleware[Message]):
    type = 'callback'
    server: ServerConnection = None
    bot: Bot

    def __init__(self, event: dict, view):
        super().__init__(event, view)

    async def pre(self):
        event = Box(self.event)
        userdata = await self.__class__.server.send(Packet(11100, vk_id=self.event.from_id))

        if not userdata.payload:
            if event.object.user_id in Config.server_config.VK.admin_ids:
                await self.answer('Подключение к серверу отсутствует')
            else:
                await self.answer(
                        'Произошла ошибка подключения к серверу. '
                        'Обратитесь к администраторам '
                        '([id508214061|Сева Чел], [id361332053|Рома Романов])')
            self.stop()

        else:
            userdata = UserModel.validate(userdata.payload)
            self.send(
                    {
                        'server': self.__class__.server,
                        'userdata': userdata,
                        'localization': Config.localizations[userdata.language_code],
                        'payload': Box(event.object.payload),
                        'bot': self.__class__.bot,
                    })

    async def answer(self, text: str):
        await Config.bot_api.messages.send(
                peer_id=self.event['object']['peer_id'],
                random_id=0,
                message=text)
