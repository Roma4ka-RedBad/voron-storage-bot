from vkbottle import load_blueprints_from_package
from vkbottle.bot import Bot

from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from misc.server import Server
from middlewares import registrate_middlewares

import asyncio


async def main():
    server = Server('http://127.0.0.1:8910')
    config = await server.send_message('config')
    server.timezone = timezone(config.content.SERVER.timezone)

    scheduler = AsyncIOScheduler()
    scheduler.start()

    bot = Bot(token=config.content.VK.bot_token)
    await registrate_middlewares(bot, server, scheduler)
    for blueprint in load_blueprints_from_package('blueprints'):
        blueprint.load(bot)

    await bot.run_polling()
 

if __name__ == '__main__':
    asyncio.run(main())
