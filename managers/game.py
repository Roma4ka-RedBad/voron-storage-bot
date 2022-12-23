import re
import asyncio
import traceback

from box import Box
from json import loads
from pathlib import Path
from bs4 import BeautifulSoup

from misc.utils import async_req
from misc.handlers import Handlers
from managers.instruments.supercell_server import SupercellServer
from managers.instruments.market_scraper import MarketScraper


class GameManager:
    def __init__(self, server_connection: tuple, messengers_manager):
        self.server = SupercellServer(*server_connection)
        self.handlers = Handlers(self, messengers_manager)

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

        self.handlers.init_handlers()

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
                game_data = await self.server_data(version[0], version[1], 1)
                if game_data.server_code == 10 and not maintenance_started:
                    maintenance_started = True
                    game_data.maintenance_end = False
                    yield game_data

                if maintenance_started and game_data.server_code != 10:
                    maintenance_started = False
                    game_data.maintenance_end = True
                    game_data.server_code = 10
                    yield game_data

                if game_data.server_code == 7:
                    if game_data.fingerprint.version != actual_version:
                        actual_version = game_data.fingerprint.version
                        yield game_data

                if game_data.server_code == 8:
                    yield game_data
                    version = (await self.get_market_data(1)).version.split('.')
            except:
                print(f'Ошибка в хендлере версий! Traceback: {traceback.format_exc()}')

            await asyncio.sleep(3)

    async def get_release_notes(self):
        request = await async_req("https://blog.brawlstars.com/blog/", "text")
        soup = BeautifulSoup(request, 'lxml')
        links = [block.find_next("a", {"data-category": "Home"}).attrs['href'] for block in
                 soup.find_all("div", {"class": "home-news-primary-item-holder"})]
        return links

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
        if re.search(search_query, 'fingerprint.json'):
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
