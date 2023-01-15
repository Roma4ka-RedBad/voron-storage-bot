from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart
from misc.middleware import Middleware

from .start import command_start
from .set_name import command_setname
from .set_name.wait_name import state_waitname
from .profile import command_profile
from .profile.set_lang_callback import profile_set_language
from .fingers import command_fingers
from .markets import command_markets
from .download import command_download
from .download.download_archive_callback import download_archive
from .working import command_working
from .working.compressed_photos import compressed_photo
from .error import error_handler

from misc.states import UserStates
from keyboards.profile import ProfileCallback
from keyboards.download import DownloadCallback


def create_public_router(bot: Bot, server) -> Router:
    public_router: Router = Router(name="public_router")
    middleware = Middleware(bot, server)

    public_router.message.middleware(middleware)
    public_router.callback_query.middleware(middleware)
    public_router.errors.middleware(middleware)
    public_router.errors.register(error_handler)

    public_router.message.register(command_start, CommandStart())
    public_router.message.register(command_setname, Command("set_name"))
    public_router.message.register(state_waitname, UserStates.wait_name)
    public_router.message.register(command_profile, Command("profile"))
    public_router.callback_query.register(profile_set_language, ProfileCallback.filter(F.action == "set_language"))
    public_router.message.register(command_fingers, Command("fingers"))
    public_router.message.register(command_markets, Command("markets"))
    public_router.message.register(command_download, Command("download"))
    public_router.callback_query.register(download_archive, DownloadCallback.filter(F.action == "archive"))
    public_router.message.register(command_working, F.document)
    public_router.message.register(compressed_photo, F.photo)

    return public_router
