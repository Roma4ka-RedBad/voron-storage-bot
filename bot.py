import asyncio
import logging

from pytz import timezone
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

from handlers import register_routers
from misc.models.server import Server

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-5s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting app")

    server = Server('http://127.0.0.1:8910')
    config = await server.send_msg('config')
    server.timezone = timezone(config.content.SERVER.timezone)
    scheduler = AsyncIOScheduler()
    storage = MemoryStorage()

    bot = Bot(token=config.content.TG.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)
    register_routers(dp, server, bot, scheduler)

    # start
    try:
        await bot.get_updates(-1)
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        await storage.close()
        await server.close()
        scheduler.shutdown()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
