import re
import asyncio

from loguru import logger
from bson import json_util
from box import Box
from pathlib import Path
from bs4 import BeautifulSoup

from misc.utils import async_request, file_writer
from misc.handlers import Handlers
from managers.instruments.supercell_server import SupercellServer
from managers.instruments.market_scraper import MarketScraper


class GameManager:
    def __init__(self, server_connection: tuple, connections_manager):
        self.server = SupercellServer(*server_connection)
        self.handlers = Handlers(self, connections_manager)
        self.data = Box()

    async def _init(self):
        app_store = await self.server_data(1, 1, 1, market_type=1)
        playmarket = await self.server_data(1, 1, 1, market_type=2)
        if playmarket.server_code == 8:
            self.data.appstore_url = app_store.download_game_link
            self.data.playmarket_url = playmarket.download_game_link

        version = (await self.get_market_data(1)).version.split('.')
        game_data = await self.server_data(int(version[0]), int(version[1]), 1)
        if game_data.server_code == 7:
            self.data.assets_url = game_data.assets_link

        self.handlers.init_handlers()

    async def server_data(self, *args, use_sync: bool = True, **kwargs):
        message = await self.server.encode_client_message(*args, **kwargs)
        if use_sync:
            message = await asyncio.to_thread(self.server.send_message_sync, message)
        else:
            message = await self.server.send_message(message)
        game_data = await self.server.decode_server_message(message)
        if game_data.server_code == 7:
            game_data.fingerprint = json_util.loads(game_data.fingerprint)
        return game_data

    async def handle_server_update(self, actual_version: str = None):
        version = actual_version.split('.')
        maintenance_started = False

        while True:
            try:
                game_data = await self.server_data(version[0], version[1], 1)
                if game_data.server_code == 10 and not maintenance_started:
                    maintenance_started = True
                    game_data.maintenance_is_end = False
                    yield game_data

                if maintenance_started and game_data.server_code != 10:
                    maintenance_started = False
                    game_data.maintenance_is_end = True
                    game_data.server_code = 10
                    yield game_data

                if game_data.server_code == 7:
                    pass
                    if game_data.fingerprint.version != actual_version:
                        actual_version = game_data.fingerprint.version
                        yield game_data

                if game_data.server_code == 8:
                    yield game_data
                    version = (await self.get_market_data(1)).version.split('.')
            except GeneratorExit as e:
                raise e
            except:
                logger.opt(exception=True).error("Handler of versions error!")

            await asyncio.sleep(3)

    async def get_release_notes(self):
        request_ru = await async_request("https://blog.brawlstars.com/ru/blog/", "text")
        request_en = await async_request("https://blog.brawlstars.com/blog/", "text")
        links = {
            'en': [block.find_next("a", {"data-category": "Home"}).attrs['href'] for block in
                   BeautifulSoup(request_en, 'lxml').find_all("div", {"class": "home-news-primary-item-holder"})],
            'ru': [block.find_next("a", {"data-category": "Home"}).attrs['href'] for block in
                   BeautifulSoup(request_ru, 'lxml').find_all("div", {"class": "home-news-primary-item-holder"})]
        }
        return links

    async def download_file(self, fingerprint_sha: str, file_name: str, result_path: Path = None, return_type="bytes"):
        request = await async_request(f"{self.data.assets_url}/{fingerprint_sha}/{file_name}", return_type)
        if result_path:
            result_path = str((result_path / file_name.split('/')[-1]).resolve())
            return await asyncio.to_thread(file_writer, result_path, request)
        else:
            return request

    async def search_files(self, search_query: str, fingerprint_sha: str):
        fingerprint = await self.download_file(fingerprint_sha, 'fingerprint.json', return_type="json")
        result = []
        if fingerprint:
            if re.findall(search_query, 'fingerprint.json'):
                result.append('fingerprint.json')

            for file in fingerprint['files']:
                try:
                    if re.findall(search_query, file['file']):
                        result.append(file['file'])
                except re.error:
                    break

        return result

    async def get_market_data(self, market_type: int, language_code: str = "ru", country: str = "us"):
        game_data = None
        if market_type == 2:
            app_id = self.data.playmarket_url.split('=')[-1]
            game_data = await MarketScraper.get_google_app_details(app_id, lang=language_code, country=country)
        elif market_type == 1:
            app_id = self.data.appstore_url.split('id')[-1]
            game_data = await MarketScraper.get_itunes_app_details(app_id, country=country)

        return Box(game_data)
