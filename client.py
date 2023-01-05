from loguru import logger
from packets import packets
from packets.base import Packet
import asyncio


class TransportRequest(asyncio.Protocol):
    def __init__(self, packet: Packet, future: asyncio.Future, no_answer: bool):
        self.encoded_data = packet.encode()
        self.no_answer = no_answer
        self.future = future

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        self.transport.write(self.encoded_data)
        if self.no_answer:
            self.transport.close()
            self.future.set_result(None)

    def data_received(self, data: bytes):
        self.transport.close()
        self.future.set_result(data.decode().strip("#"))

    def connection_lost(self, exc: Exception | None):
        if not self.future.done():
            self.future.set_result(False)


class EventsHandler(asyncio.Protocol):
    def __init__(self, is_closing: asyncio.Future, instance):
        self.is_closing = is_closing
        self.server_instance = instance
        self.loop = asyncio.get_running_loop()

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        transport.write(Packet(10100).encode())
        transport.write(Packet(10101).encode())
        logger.info(f"Server connected!")

    def data_received(self, data: bytes):
        raw_packets = data.decode().split("#")
        for raw_packet in raw_packets:
            if raw_packet:
                packet = Packet.decode(raw_packet)
                if packet.pid == 10100:
                    self.transport_id = packet.payload.transport_id
                elif packet.pid == 10101:
                    self.config_data = packet.payload
                else:
                    self.loop.create_task(packets[packet.pid](self, packet))

    def connection_lost(self, exc: Exception | None):
        self.is_closing.set_result(True)
        logger.warning('The server closed the connection!')

    def is_connected(self) -> bool:
        return not self.transport.is_closing()

    def get_transport_id(self) -> int:
        return getattr(self, "transport_id", None)

    def get_config_data(self):
        return getattr(self, "config_data", None)


class ServerConnection:
    def __init__(self, host: str, port: int, reconnect_timeout: int = 3):
        self.server_host = host
        self.server_port = port
        self.reconnect_timeout = reconnect_timeout
        self.loop = asyncio.get_running_loop()
        self.events_handler = None

    async def send(self, packet: Packet, no_answer: bool = False, get_decoded_packet: bool = True):
        if await self.is_connected():
            try:
                result = self.loop.create_future()
                await self.loop.create_connection(
                    lambda: TransportRequest(packet, result, no_answer),
                    self.server_host, self.server_port)
                result = await result

                if get_decoded_packet and result:
                    return Packet.decode(result)
                else:
                    return result
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
                if data := self.events_handler.get_config_data():
                    return data.config.TG.token

            await asyncio.sleep(self.reconnect_timeout)
