import asyncio
import inspect
from loguru import logger

from managers.connections import ConnectionsManager
from managers.game import GameManager

from packets import packets
from packets.base import Packet


class Server(asyncio.Protocol):
    def __init__(self, connections_manager: ConnectionsManager, game_manager: GameManager):
        self.connections = connections_manager
        self.game_manager = game_manager

    def connection_made(self, transport: asyncio.Transport):
        self.client_connection = self.connections.register(transport)

    def data_received(self, data: bytes):
        raw_packets = data.decode().split("#")
        for raw_packet in raw_packets:
            if raw_packet:
                packet = Packet.decode(raw_packet)
                logger.debug(f"[{packet.pid}] Received packet!")
                asyncio.create_task(self._start_task(packets[packet.pid], packet=packet))

    async def _start_task(self, func, **kwargs):
        func_args = inspect.getfullargspec(func)
        new_kwargs = {}
        for name in func_args.args:
            if arg_data := kwargs.get(name, None):
                new_kwargs.update({name: arg_data})

        for name, data in func_args.annotations.items():
            for arg_name, arg_data in kwargs.items():
                if isinstance(arg_data, data) and not new_kwargs.get(arg_name, None):
                    new_kwargs.update({name: arg_data})

        try:
            await func(self, **new_kwargs)
        except:
            logger.opt(exception=True).error("Error in task starter!")

    def connection_lost(self, exc: Exception | None):
        self.connections.remove(self.client_connection)


async def main():
    loop = asyncio.get_running_loop()

    connections_manager = ConnectionsManager()
    game_manager = GameManager(("game.brawlstarsgame.com", 9339), connections_manager)
    await game_manager._init()
    for handler in game_manager.handlers.handlers:
        loop.create_task(handler)

    server = await loop.create_server(lambda: Server(connections_manager, game_manager), '127.0.0.1', 8888)

    logger.info("Server running!")
    async with server:
        await server.serve_forever()


asyncio.run(main())
