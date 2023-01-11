import asyncio
from packets.base import Packet
from loguru import logger
from .event_handler import EventsHandler
from .transport_request import TransportRequest


class ServerConnection:
    def __init__(self, host: str, port: int, reconnect_timeout: int = 3):
        self.server_host = host
        self.server_port = port
        self.reconnect_timeout = reconnect_timeout
        self.loop = asyncio.get_running_loop()
        self.events_handler = None

    async def send(self, packet: Packet, no_answer: bool = False):
        if await self.is_connected():
            try:
                result = self.loop.create_future()
                await self.loop.create_connection(
                    lambda: TransportRequest(packet, result, no_answer),
                    self.server_host, self.server_port)
                return await result
            except:
                logger.opt(exception=True).error("Exception in send function!")
        else:
            return False

    async def _reconnect(self):
        while True:
            try:
                is_closing = self.loop.create_future()
                self.events_handler = await self.loop.create_connection(lambda: EventsHandler(is_closing, self),
                                                                        self.server_host, self.server_port)
                self.events_handler = self.events_handler[1]
                await is_closing
            except:
                logger.warning("Connection failed!")
                await asyncio.sleep(self.reconnect_timeout)

    async def connect(self):
        self.loop.create_task(self._reconnect())

    async def is_connected(self):
        if self.events_handler:
            return self.events_handler.is_connected()

    async def get_bot_token(self) -> str:
        while True:
            if await self.is_connected():
                if self.events_handler.config_data:
                    return self.events_handler.config_data.config.TG.token

            await asyncio.sleep(self.reconnect_timeout)
