import asyncio
import sys

from loguru import logger
from vkbottle import Bot

from bot_config import Config
from misc.connections import ServerConnection
from middlewares import registrate_middlewares

import blueprints


async def main():
    server = ServerConnection('127.0.0.1', 8910)
    await Config.init(server, blueprints.__all__)
    logger.remove()
    logger.add(sys.stderr, level='INFO')
    bot = Bot(api=Config.bot_api, state_dispenser=Config.state_dispenser)

    for labeler in Config.labelers.__all__():
        bot.labeler.load(labeler)

    await registrate_middlewares(bot, server)

    try:
        await bot.run_polling()
    except (SystemExit, KeyboardInterrupt):
        print('Бот остановлен')
        raise SystemExit


asyncio.run(main())
