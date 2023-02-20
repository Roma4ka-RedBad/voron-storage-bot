from vkbottle import API
from vkbottle.bot import Bot


from misc.connections import ServerConnection
from .add_context import AddArgumentsToCallbackEventMiddleware, AddArgumentsToMessageEventMiddleware

middlewares = [AddArgumentsToMessageEventMiddleware, AddArgumentsToCallbackEventMiddleware]


async def registrate_middlewares(dispatcher: Bot, server: ServerConnection):
    for middleware in middlewares:
        middleware.server = server
        middleware.bot = dispatcher

        if middleware.type == 'message':
            dispatcher.labeler.message_view.register_middleware(middleware)
        elif middleware.type == 'callback':
            dispatcher.labeler.raw_event_view.register_middleware(middleware)
