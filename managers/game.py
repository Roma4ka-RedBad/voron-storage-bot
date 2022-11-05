import asyncio
import socket
import requests

from box import Box
from json import loads
from database import FingerprintTable
from managers.instruments.bytestream import Reader, Writer

from google_play_scraper.scraper import PlayStoreScraper
from itunes_app_scraper.scraper import AppStoreScraper  # async-itunes-app-scraper-dmi


class SupercellServer:
    def __init__(self, ip_address: str, ip_port: int):
        self.address = (ip_address, ip_port)

    def send_message(self, message):
        server = socket.create_connection(self.address)
        server.send(message.buffer)
        header = server.recv(7)
        packet_length = int.from_bytes(header[2:5], 'big')
        received_data = b''
        while packet_length > 0:
            data = server.recv(packet_length)
            if not data:
                break
            received_data += data
            packet_length -= len(data)
        server.close()
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

        message.write_int(major_v, 32, False)
        message.write_int(revision_v, 32, False)
        message.write_int(build_v, 32, False)

        message.write_string(content_hash, 32)  # content hash
        message.write_int(market_type, 32, False)  # device type
        message.write_int(market_type, 32, False)  # app store

        if with_pcode:
            return self.put_packet_code(message, 10100)

        return message


class GameManager:
    def __init__(self, server_connection: tuple):
        self.server = SupercellServer(*server_connection)

    async def init_prod_handler(self):
        version = FingerprintTable.get_or_none(is_actual=True)
        if version:
            version = f"{version.major_v}.{version.build_v}.{version.revision_v}"

        async for game_data in self.handle_server_update(version):
            raw_version = game_data.fingerprint.version.split('.')
            print('New version!')
            if (FingerprintTable.get(is_actual=True)).sha != game_data.fingerprint.sha:
                FingerprintTable.update(is_actual=False).where(FingerprintTable.is_actual == True).execute()
                FingerprintTable.get_or_create(sha=game_data.fingerprint.sha, major_v=raw_version[0],
                                               build_v=raw_version[1], revision_v=raw_version[2])
            else:
                print('Skipping...')

    async def server_data(self, *args, **kwargs):
        message = self.server.encode_client_message(*args, **kwargs)
        message = self.server.send_message(message)
        game_data = self.server.decode_server_message(message)
        if game_data.server_code == 7:
            game_data.fingerprint = loads(game_data.fingerprint)
        return game_data

    async def handle_server_update(self, actual_version: str = None):
        maintenance_started = False
        while True:
            app = (await self.get_market_data(1)).version.split('.')
            game_data = await self.server_data(int(app[0]), int(app[1]), 1)
            if game_data.server_code == 10 and not maintenance_started:
                maintenance_started = True
                yield game_data

            if game_data.server_code == 7:
                maintenance_started = False
                if game_data.fingerprint.version != actual_version:
                    actual_version = game_data.fingerprint.version
                    yield game_data

            await asyncio.sleep(3)

    async def download_file(self, fingerprint_sha: str, name: str):
        app = (await self.get_market_data(1)).version.split('.')
        game_data = await self.server_data(int(app[0]), int(app[1]), 1)
        if fingerprint_sha == 'actual':
            fingerprint_sha = game_data.fingerprint.sha

        request = requests.get(f"{game_data.assets_link}/{fingerprint_sha}/{name}")
        return request

    async def get_market_data(self, market_type: int, language_code: str = 'ru', country: str = 'us'):
        game_data = await self.server_data(1, 1, 1, market_type=market_type)
        if game_data.server_code == 8:
            if market_type == 2:
                app_id = game_data.download_game_link.split('=')[-1]
                app = PlayStoreScraper()
                game_data = await app.get_app_details(app_id, lang=language_code, country=country)
            elif market_type == 1:
                app_id = game_data.download_game_link.split('id')[-1]
                app = AppStoreScraper()
                game_data = await app.get_app_details(app_id, lang=language_code, country=country)

            return Box(game_data)
