from vkbottle import API
from vkbottle.bot import Bot

from misc.models.scheduler import Scheduler
from misc.models.server import Server
from .add_context import AddArgumentsToCallbackEventMiddleware, AddArgumentsToMessageEventMiddleware

middlewares = [AddArgumentsToMessageEventMiddleware, AddArgumentsToCallbackEventMiddleware]


async def registrate_middlewares(dispatcher: Bot, server: Server, scheduler: Scheduler):
    localizations = await server.send_message('user/localization/*')
    config = await server.send_message('config')

    for middleware in middlewares:
        middleware.server = server
        middleware.scheduler = scheduler
        middleware.localizations = localizations.content
        middleware.bot = dispatcher
        middleware.config = config.content
        middleware.user_api = API(token=config.content.VK.user_token)

        if middleware.type == 'message':
            dispatcher.labeler.message_view.register_middleware(middleware)
        elif middleware.type == 'callback':
            dispatcher.labeler.raw_event_view.register_middleware(middleware)
