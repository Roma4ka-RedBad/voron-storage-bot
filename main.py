from vkbottle import load_blueprints_from_package
from vkbottle.bot import Bot

from pytz import timezone

from misc.models.server import Server
from misc.models.scheduler import Scheduler
from middlewares import registrate_middlewares

import asyncio


async def main():
    server = Server('http://127.0.0.1:8910')
    config = await server.send_message('config')
    server.timezone = timezone(config.content.SERVER.timezone)

    bot = Bot(token=config.content.VK.bot_token)
    await registrate_middlewares(bot, server)
    for blueprint in load_blueprints_from_package('blueprints'):
        blueprint.load(bot)

    try:
        await bot.run_polling()
    except (SystemExit, KeyboardInterrupt):
        await server.close()
        print('Бот остановлен')
 

if __name__ == '__main__':
    asyncio.run(main())
