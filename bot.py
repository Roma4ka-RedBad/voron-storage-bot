import asyncio
import aiohttp
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

from handlers import register_routers
from misc.server import Server

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-5s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting app")

    server = Server('http://192.168.0.127:8910')
    config = await server.send_message('config')
    storage = MemoryStorage()

    bot = Bot(token=config.TG.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)
    register_routers(dp, server, bot)

    # start
    try:
        await bot.get_updates(-1)
        await dp.start_polling(bot)
    finally:
        await storage.close()
        await server.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
