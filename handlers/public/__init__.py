from aiogram import Router, Bot, F
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from middlewares.base import InitMiddleware
from misc.models.server import Server

from .start.base import command_start
from .profile.base import command_profile
from .set_name.base import command_setname
from .set_name.wait_name import setname_waitname
from .work.base import command_work
from .work.callbacks.show_filename import work_show_filename
from .work.callbacks.by_archive import work_by_archive
from .work.callbacks.convert import work_convert

from states.user import UserStates

from keyboards.work import WorkCallback


def create_public_router(server: Server, bot: Bot, scheduler: AsyncIOScheduler) -> Router:
    public_router: Router = Router(name="public_router")

    # Сообщения

    public_router.message.middleware(InitMiddleware(server, bot, scheduler))
    public_router.callback_query.middleware(InitMiddleware(server, bot, scheduler))

    public_router.message.register(command_start, commands=["start"])
    public_router.message.register(command_profile, commands=["profile"])
    public_router.message.register(command_setname, commands=["set_name"])
    public_router.message.register(setname_waitname, UserStates.wait_name)
    public_router.message.register(command_work, content_types=['document'])
    public_router.callback_query.register(work_show_filename, WorkCallback.filter(F.action == "show_filename"))
    public_router.callback_query.register(work_by_archive, WorkCallback.filter(F.action == "by_archive"))
    public_router.callback_query.register(work_convert, WorkCallback.filter(F.action == "convert"))
    return public_router
