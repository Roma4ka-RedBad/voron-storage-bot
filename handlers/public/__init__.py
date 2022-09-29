from aiogram import Router, Bot, F

from middlewares.init_contexts import InitMiddleware
from misc.server import Server

from .start.base import command_start
from .work.base import command_work
from .work.callbacks.show_filename import work_show_filename

from keyboards.work import WorkCallback


def create_public_router(server: Server, bot: Bot) -> Router:
    public_router: Router = Router(name="public_router")

    # Сообщения

    public_router.message.middleware(InitMiddleware(server, bot))
    public_router.message.register(command_start,
                                   commands=["start"])
    public_router.message.register(command_work, content_types=['document'])
    public_router.callback_query.register(work_show_filename, WorkCallback.filter(F.action == "show_filename"))
    return public_router
