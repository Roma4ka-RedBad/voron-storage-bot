from .add_context import AddArgumentsToCallbackEventMiddleware, AddArgumentsToMessageEventMiddleware

from vkbottle.bot import Bot
from misc.server import Server
from apscheduler.schedulers.asyncio import AsyncIOScheduler

middlewares = [AddArgumentsToMessageEventMiddleware, AddArgumentsToCallbackEventMiddleware]


async def registrate_middlewares(dispatcher: Bot, server: Server, scheduler: AsyncIOScheduler):
    localizations = await server.send_message('localization/*')
    config = await server.send_message('config')

    for middleware in middlewares:
        middleware.server = server
        middleware.scheduler = scheduler
        middleware.localizations = localizations.content
        middleware.bot = dispatcher
        middleware.config = config.content

        if middleware.type == 'message':
            dispatcher.labeler.message_view.register_middleware(middleware)
        elif middleware.type == 'callback':
            dispatcher.labeler.raw_event_view.register_middleware(middleware)
