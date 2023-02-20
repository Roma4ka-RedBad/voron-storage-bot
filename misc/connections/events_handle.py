import asyncio
from io import BytesIO

from loguru import logger

from misc.bytestream import Reader
from misc.packets import packets
from misc.packets import Packet


class EventsHandler(asyncio.Protocol):
    def __init__(self, is_closing: asyncio.Future, instance):
        self.is_closing = is_closing
        self.server_instance = instance
        self.loop = asyncio.get_running_loop()
        self.sub_buffer = BytesIO()

        self.transport = None
        self.transport_id = None
        self.config_data = None

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        transport.write(Packet(10100).encode())
        transport.write(Packet(10101).encode())
        logger.info(f"Server connected!")

    def decode_packets(self, data: bytes):
        decompressed_data = Reader.decompress_data(self.sub_buffer.getvalue() + data)
        if not decompressed_data:
            self.sub_buffer.write(data)
        else:
            self.sub_buffer = BytesIO()

        while len(decompressed_data) > 0:
            reader = Reader(decompressed_data)
            header = reader.read(7)
            packet_id = int.from_bytes(header[:2], 'big')
            packet_length = int.from_bytes(header[2:5], 'big')
            packet_payload = Reader(reader.read(packet_length))
            yield Packet(packet_id, packet_payload.read_string(32))
            decompressed_data = reader.read()

    def data_received(self, data: bytes):
        for packet in self.decode_packets(data):
            if packet.pid == 10100:
                self.transport_id = packet.payload.transport_id
            elif packet.pid == 10101:
                self.config_data = packet.payload
            else:
                if packet.pid in packets:
                    self.loop.create_task(packets[packet.pid](self, packet))

    def connection_lost(self, exc: Exception | None):
        self.is_closing.set_result(True)
        logger.warning('The server closed the connection!')

    def is_connected(self) -> bool:
        return not self.transport.is_closing()
