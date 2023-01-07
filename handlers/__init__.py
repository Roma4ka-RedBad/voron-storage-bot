from aiogram import Router, Bot, F
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
from .working.compressed_photos import compressed_photo

from misc.states import UserStates
from keyboards.profile import ProfileCallback
from keyboards.download import DownloadCallback


def create_public_router(bot: Bot, server) -> Router:
    public_router: Router = Router(name="public_router")
    middleware = Middleware(bot, server)

    public_router.message.middleware(middleware)
    public_router.callback_query.middleware(middleware)
    public_router.message.register(command_start, commands=["start"])
    public_router.message.register(command_setname, commands=["set_name"])
    public_router.message.register(state_waitname, UserStates.wait_name)
    public_router.message.register(command_profile, commands=["profile"])
    public_router.callback_query.register(profile_set_language, ProfileCallback.filter(F.action == "set_language"))
    public_router.message.register(command_fingers, commands=["fingers"])
    public_router.message.register(command_markets, commands=["markets"])
    public_router.message.register(command_download, commands=["download"])
    public_router.callback_query.register(download_archive, DownloadCallback.filter(F.action == "archive"))
    public_router.message.register(compressed_photo, content_types=['photo'])

    return public_router
