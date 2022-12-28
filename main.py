import asyncio
import sys

from loguru import logger
from vkbottle import Bot

from blueprints import labelers
from config import bot_config
from middlewares import registrate_middlewares
from misc.models.scheduler import Scheduler

labelers = labelers


async def main():
    logger.remove()
    logger.add(sys.stderr, level='INFO')
    bot = Bot(api=bot_config.api, state_dispenser=bot_config.state_dispenser)
    for labeler in bot_config.labelers.__all__():
        bot.labeler.load(labeler)

    await registrate_middlewares(
        bot,
        bot_config.server,
        Scheduler(bot_config.scheduler, bot_config.server.timezone))

    try:
        bot_config.scheduler.start()
        await bot.run_polling()
    except (SystemExit, KeyboardInterrupt):
        bot_config.scheduler.shutdown()
        print('Бот остановлен')
        raise SystemExit


asyncio.run(main())
