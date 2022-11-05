import asyncio
import requests

from box import Box
from json import loads
from database import FingerprintTable
from managers.instruments.supercell_server import SupercellServer

from google_play_scraper.scraper import PlayStoreScraper
from itunes_app_scraper.scraper import AppStoreScraper  # async-itunes-app-scraper-dmi


class GameManager:
    def __init__(self, server_connection: tuple):
        self.server = SupercellServer(*server_connection)

    async def init_prod_handler(self):
        version = FingerprintTable.get_or_none(is_actual=True)
        if version:
            version = f"{version.major_v}.{version.build_v}.{version.revision_v}"

        async for game_data in self.handle_server_update(version):
            raw_version = game_data.fingerprint.version.split('.')
            if actual_sha := FingerprintTable.get_or_none(is_actual=True):
                actual_sha = actual_sha.sha

            print('New version!')
            if actual_sha != game_data.fingerprint.sha:
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
