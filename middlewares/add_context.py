from vkbottle import BaseMiddleware
from vkbottle.bot import Message, Bot

from misc.server import Server
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from json import loads
from box import Box
from random import randint


class AddArgumentsToMessageEventMiddleware(BaseMiddleware[Message]):
    type = 'message'
    server: Server = None
    scheduler: AsyncIOScheduler = None
    localizations: dict | Box
    config: dict | Box

    def __init__(self, event: Message, view):
        super().__init__(event, view)

    async def pre(self):
        # Документация говорит обращаться к аттрибутам класса через self.__class__
        userdata = await self.__class__.server.send_message(
            'user/get', {
                'vk_id': self.event.from_id
                })

        if userdata is None:
            if self.event.from_id in [508214061, 361332053]:
                await self.event.answer('Подключение к серверу отсутствует')
            else:
                await self.event.answer(
                    'Произошла ошибка подключения к серверу. '
                    'Обратитесь к администраторам '
                    '([id508214061|Сева Чел], [id361332053|Рома Романов])')
            self.stop()

        else:
            payload = Box(loads(self.event.payload)) if self.event.payload else self.event.payload
            self.send(
                {
                    'server': self.__class__.server,
                    'scheduler': self.__class__.scheduler,
                    'userdata': userdata.content.__data__,
                    'localization': self.__class__.localizations[
                        userdata.content.__data__.language_code],
                    'config': self.__class__.config,
                    'payload': payload
                    })


class AddArgumentsToCallbackEventMiddleware(BaseMiddleware[Message]):
    type = 'callback'
    server: Server = None
    scheduler: AsyncIOScheduler = None
    localizations: dict | Box
    config: dict | Box
    bot: Bot  # callback event не типизирован, поэтому для запросов к вк апи я это необходимо

    def __init__(self, event: dict, view):
        super().__init__(event, view)

    async def pre(self):
        event = Box(self.event)
        userdata = await self.__class__.server.send_message(
            'user/get', {
                'vk_id': event.object.user_id
                })

        if userdata is None:
            if event.object.user_id in [508214061, 361332053]:
                await self.answer('Подключение к серверу отсутствует')
            else:
                await self.answer(
                    'Произошла ошибка подключения к серверу. '
                    'Обратитесь к администраторам '
                    '([id508214061|Сева Чел], [id361332053|Рома Романов])')
            self.stop()

        else:
            self.send(
                {
                    'server': self.__class__.server,
                    'scheduler': self.__class__.scheduler,
                    'userdata': userdata.content.__data__,
                    'localization': self.__class__.localizations[
                        userdata.content.__data__.language_code],
                    'config': self.__class__.config,
                    'payload': Box(event.object.payload)
                    })

    async def answer(self, text: str):
        await self.bot.api.messages.send(
            peer_id=self.event['object']['peer_id'],
            random_id=randint(1234, 5678),
            message=text)