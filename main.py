import asyncio
import inspect
import traceback
from loguru import logger

from managers.connections import ConnectionsManager
from managers.game import GameManager
from managers.file_storage import FileManager
from misc.bytestream import Reader

from packets import packets
from packets.base import Packet


class Server(asyncio.Protocol):
    def __init__(self, connections_manager: ConnectionsManager, game_manager: GameManager, file_manager: FileManager):
        self.connections = connections_manager
        self.game_manager = game_manager
        self.file_manager = file_manager

        self.client_connection = None

    def connection_made(self, transport: asyncio.Transport):
        self.client_connection = self.connections.register(transport)

    def decode_packets(self, data: bytes):
        data = Reader.decompress_data(data)
        while len(data) > 0:
            reader = Reader(data)
            header = reader.read(7)
            packet_id = int.from_bytes(header[:2], 'big')
            packet_length = int.from_bytes(header[2:5], 'big')
            packet_payload = Reader(reader.read(packet_length))
            yield Packet(packet_id, packet_payload.read_string(32))
            data = reader.read()

    def data_received(self, data: bytes):
        for packet in self.decode_packets(data):
            if packet.pid in packets:
                logger.debug(f"[{packet.pid}] Received packet!")
                asyncio.create_task(self._start_task(packets[packet.pid], packet=packet, game_manager=self.game_manager,
                                                     connections_manager=self.connections,
                                                     file_manager=self.file_manager))

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
            await packets[12100](self, Packet(12100), self.connections, traceback.format_exc())
            logger.opt(exception=True).error("Error in task starter!")

    def connection_lost(self, exc: Exception | None):
        self.connections.remove(self.client_connection)


async def main():
    loop = asyncio.get_running_loop()

    connections_manager = ConnectionsManager()
    file_manager = FileManager(connections_manager)
    game_manager = GameManager(("game.brawlstarsgame.com", 9339), connections_manager)
    file_manager.scheduler.start()
    await game_manager.init()
    for handler in game_manager.handlers.handlers:
        loop.create_task(handler)

    server = await loop.create_server(lambda: Server(connections_manager, game_manager, file_manager), '127.0.0.1',
                                      8888)

    logger.info("Server running!")
    async with server:
        await server.serve_forever()


asyncio.run(main())
