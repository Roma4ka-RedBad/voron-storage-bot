import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from misc.my_logger import LoguruHandler
from misc.connections import ServerConnection
from handlers import create_public_router


async def main():
    logging.basicConfig(
        handlers=[LoguruHandler()],
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-5s [%(asctime)s] - %(name)s - %(message)s',
    )

    server = ServerConnection('127.0.0.1', 8888)
    await server.connect()
    bot = Bot(token=await server.get_bot_token(), parse_mode='HTML',
              session=AiohttpSession(api=TelegramAPIServer.from_base("http://localhost:8080", is_local=True)))
    dp = Dispatcher()
    dp.include_router(create_public_router(bot, server))

    try:
        await bot.get_updates()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


asyncio.run(main())
