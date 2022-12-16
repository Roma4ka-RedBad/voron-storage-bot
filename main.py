import asyncio
import uvicorn
import colorama
from fastapi import FastAPI

from routers import user_router, files_router, commands_data_router, about_router
from misc.middleware import VoronStorageMiddleware

from managers.game import GameManager
from managers.queues import QueueManager
from managers.convert import ConvertManager
from managers.messengers import MessengersManager


async def main():
    app = FastAPI()
    queue_manager = QueueManager()
    convert_manager = ConvertManager(queue_manager)
    messengers_manager = MessengersManager()
    game_manager = GameManager(("game.brawlstarsgame.com", 9339), messengers_manager)

    await queue_manager._init()
    await game_manager._init()
    for core in convert_manager.queue.cores:
        asyncio.create_task(core)
    for handler in game_manager.handlers.handlers:
        asyncio.create_task(handler)

    app.add_middleware(VoronStorageMiddleware, queue_manager=queue_manager, convert_manager=convert_manager,
                       game_manager=game_manager, messengers_manager=messengers_manager)
    app.include_router(user_router)
    app.include_router(files_router)
    app.include_router(commands_data_router)
    app.include_router(about_router)

    server_config = uvicorn.Config(app, host='127.0.0.1', port=8910, use_colors=True, access_log=True)
    server = uvicorn.Server(server_config)
    await server.serve()


if __name__ == '__main__':
    colorama.init()
    asyncio.run(main())
