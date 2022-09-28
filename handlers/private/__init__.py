from aiogram import Router, Bot

from middlewares.init_contexts import InitMiddleware
from misc.server import Server

from .start.base import command_start


def create_public_router(server: Server, bot: Bot) -> Router:
    private_router: Router = Router(name="public_router")

    # Сообщения

    private_router.message.middleware(InitMiddleware(server, bot))
    private_router.message.register(command_start,
                                    commands=["start"])
    return private_router
