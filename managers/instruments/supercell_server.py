import asyncio

from box import Box
from managers.instruments.bytestream import Reader, Writer


class SupercellServer:
    def __init__(self, ip_host: str, ip_port: int):
        self.ip_host = ip_host
        self.ip_port = ip_port

    async def send_message(self, message):
        receiver, sender = await asyncio.open_connection(self.ip_host, self.ip_port)
        sender.write(message.buffer)
        await sender.drain()
        header = await receiver.read(7)
        packet_length = int.from_bytes(header[2:5], 'big')
        received_data = b''
        while packet_length > 0:
            data = await receiver.read(packet_length)
            if not data:
                break
            received_data += data
            packet_length -= len(data)
        sender.close()
        await sender.wait_closed()
        return received_data

    @staticmethod
    def put_packet_code(message, server_code: int):
        message_buffer = message.buffer
        message.buffer = b''
        message.write_int(server_code, 16, False)
        message.buffer += len(message_buffer).to_bytes(3, 'big')
        message.write_int(0, 16, False)
        message.buffer += message_buffer
        return message

    @staticmethod
    def decode_server_message(message: bytes):
        reader = Reader(message)
        data = Box()

        data.server_code = reader.read_int(32, False)
        if data.server_code == 10:
            for _ in range(5):
                data[f'unk{_}'] = reader.read_int(32, False)
            data.maintenance_end_time = reader.read_int(32, False)
            for _ in range(5, 14):
                data[f'unk{_}'] = reader.read_int(32, False)
        elif data.server_code in [7, 8, 9, 16]:
            data.fingerprint = reader.read_string(32)
            data.redirect_host = reader.read_string(32)
            data.assets_link = reader.read_string(32)
            data.download_game_link = reader.read_string(32)
            data.unk1 = reader.read_string(32)
            data.unk2 = reader.read_int(32, False)
            data.unk3 = reader.read_bool()
            data.unk4 = reader.read_int(32, False)
            data.unk5 = reader.read_int(32, False)
            data.content_link = reader.read_string(32)
            data.assets2_link = reader.read_string(32)

        return data

    def encode_client_message(self, major_v: int, build_v: int, revision_v: int, content_hash: str = '',
                              market_type: int = 2, with_pcode: bool = True):
        message = Writer()

        message.write_int(0, 32, False)  # protocol version
        message.write_int(11, 32, False)  # key version

        message.write_int(int(major_v), 32, False)
        message.write_int(int(revision_v), 32, False)
        message.write_int(int(build_v), 32, False)

        message.write_string(content_hash, 32)  # content hash
        message.write_int(market_type, 32, False)  # device type
        message.write_int(market_type, 32, False)  # app store

        if with_pcode:
            return self.put_packet_code(message, 10100)

        return message
