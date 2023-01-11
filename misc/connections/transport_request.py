import asyncio
from packets.base import Packet
from io import BytesIO
from misc.bytestream import Reader


class TransportRequest(asyncio.Protocol):
    def __init__(self, packet: Packet, future: asyncio.Future, no_answer: bool):
        self.encoded_data = packet.encode()
        self.no_answer = no_answer
        self.subbuffer = BytesIO()
        self.future = future
        self.transport = None

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        self.transport.write(self.encoded_data)
        if self.no_answer:
            self.transport.close()
            self.future.set_result(None)

    def data_received(self, data: bytes):
        decompressed_data = Reader.decompress_data(self.subbuffer.getvalue() + data)
        if decompressed_data:
            self.transport.close()
            reader = Reader(decompressed_data)
            header = reader.read(7)
            packet_id = int.from_bytes(header[:2], 'big')
            packet_length = int.from_bytes(header[2:5], 'big')
            packet_payload = Reader(reader.read(packet_length))
            packet = Packet(packet_id, packet_payload.read_string(32))
            self.future.set_result(packet)
        else:
            self.subbuffer.write(data)

    def connection_lost(self, exc: Exception | None):
        if not self.future.done():
            self.future.set_result(False)
