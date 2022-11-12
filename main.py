from vkbottle import load_blueprints_from_package
from vkbottle.bot import Bot
from loguru import logger
from pytz import timezone

from misc.models.server import Server
from misc.models.scheduler import Scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares import registrate_middlewares

import asyncio
import sys


async def main():
    logger.remove()
    logger.add(sys.stderr, level='INFO')
    server = Server('http://127.0.0.1:8911')
    config = await server.send_message('config')
    server.timezone = timezone(config.content.SERVER.timezone)

    scheduler = AsyncIOScheduler()
    bot = Bot(token=config.content.VK.bot_token)
    await registrate_middlewares(bot, server, Scheduler(scheduler, timezone(config.content.SERVER.timezone)))
    for blueprint in load_blueprints_from_package('blueprints'):
        blueprint.load(bot)

    try:
        scheduler.start()
        await bot.run_polling()
    except (SystemExit, KeyboardInterrupt):
        scheduler.shutdown()
        print('Бот остановлен')
 

if __name__ == '__main__':
    asyncio.run(main())
