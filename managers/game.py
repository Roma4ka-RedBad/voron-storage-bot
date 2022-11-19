import re
import asyncio
import traceback

from box import Box
from json import loads
from pathlib import Path
from database import FingerprintTable

from utils import async_req
from managers.instruments.supercell_server import SupercellServer
from managers.instruments.market_scraper import MarketScraper


class GameManager:
    def __init__(self, server_connection: tuple):
        self.server = SupercellServer(*server_connection)

        self.assets_url = None
        self.appstore_url = None
        self.playmarket_url = None

    async def _init(self):
        app_store = await self.server_data(1, 1, 1, market_type=1)
        playmarket = await self.server_data(1, 1, 1, market_type=2)
        if playmarket.server_code == 8:
            self.appstore_url = app_store.download_game_link
            self.playmarket_url = playmarket.download_game_link

        version = (await self.get_market_data(1)).version.split('.')
        game_data = await self.server_data(int(version[0]), int(version[1]), 1)
        if game_data.server_code == 7:
            self.assets_url = game_data.assets_link

    async def init_prod_handler(self):
        version = FingerprintTable.get_or_none(is_actual=True)
        if version:
            version = f"{version.major_v}.{version.build_v}.{version.revision_v}"
        else:
            version = (await self.get_market_data(1)).version

        async for game_data in self.handle_server_update(version):
            if game_data.server_code == 7:
                raw_version = game_data.fingerprint.version.split('.')
                if actual_sha := FingerprintTable.get_or_none(is_actual=True):
                    actual_sha = actual_sha.sha

                if actual_sha != game_data.fingerprint.sha:
                    FingerprintTable.update(is_actual=False).where(FingerprintTable.is_actual).execute()
                    FingerprintTable.get_or_create(sha=game_data.fingerprint.sha, major_v=raw_version[0],
                                                   build_v=raw_version[1], revision_v=raw_version[2])

            elif game_data.server_code == 10:
                print(f'Start maintenance! Time: {game_data.maintenance_end_time}')

    async def server_data(self, *args, **kwargs):
        message = self.server.encode_client_message(*args, **kwargs)
        message = await self.server.send_message(message)
        game_data = self.server.decode_server_message(message)
        if game_data.server_code == 7:
            game_data.fingerprint = loads(game_data.fingerprint)
        return game_data

    async def handle_server_update(self, actual_version: str = None):
        version = actual_version.split('.')
        maintenance_started = False

        while True:
            try:
                game_data = await self.server_data(int(version[0]), int(version[1]), 1)
                if game_data.server_code == 10 and not maintenance_started:
                    maintenance_started = True
                    yield game_data

                if maintenance_started and game_data.server_code != 10:
                    maintenance_started = False

                if game_data.server_code == 7:
                    if game_data.fingerprint.version != actual_version:
                        actual_version = game_data.fingerprint.version
                        yield game_data

                if game_data.server_code == 8:
                    version = (await self.get_market_data(1)).version.split('.')
            except:
                print(f'Ошибка в хендлере версий! Traceback: {traceback.format_exc()}')

            await asyncio.sleep(3)

    async def download_file(self, fingerprint_sha: str, file_name: str, result_path: Path = None, return_type='bytes'):
        request = await async_req(f"{self.assets_url}/{fingerprint_sha}/{file_name}", return_type)
        if result_path:
            result_path = (result_path / file_name.split('/')[-1]).absolute()
            with open(result_path, 'wb') as file:
                file.write(request)
                file.close()
            return result_path
        else:
            return request

    async def search_files(self, search_query: str, fingerprint_sha: str):
        fingerprint = await self.download_file(fingerprint_sha, 'fingerprint.json', return_type='json')
        result = []
        if re.search(search_query, 'fingerprint.json') :
            result.append('fingerprint.json')
        for file in fingerprint['files']:
            try:
                if re.search(search_query, file['file']):
                    result.append(file['file'])
            except re.error:
                break

        return result

    async def get_market_data(self, market_type: int, language_code: str = 'ru', country: str = 'us'):
        game_data = None
        if market_type == 2:
            app_id = self.playmarket_url.split('=')[-1]
            game_data = await MarketScraper.get_google_app_details(app_id, lang=language_code, country=country)
        elif market_type == 1:
            app_id = self.appstore_url.split('id')[-1]
            game_data = await MarketScraper.get_itunes_app_details(app_id, country=country)

        return Box(game_data)
