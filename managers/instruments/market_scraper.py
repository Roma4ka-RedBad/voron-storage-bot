import re
import json

from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from utils import async_reqget


class WebsiteMappings:
    app_detail_ds_block = 'ds:5'
    app_details_mapping = {
        'title': [app_detail_ds_block, 1, 2, 0, 0],
        'developer_name': [app_detail_ds_block, 1, 2, 68, 0],
        'developer_link': [app_detail_ds_block, 1, 2, 68, 1, 4, 2],
        'price_inapp': [app_detail_ds_block, 1, 2, 19, 0],
        'category': [app_detail_ds_block, 1, 2, 79, 0, 0, 1, 4, 2],
        'video_link': [app_detail_ds_block, 1, 2, 100, 1, 2, 0, 2],
        'icon_link': [app_detail_ds_block, 1, 2, 95, 0, 3, 2],
        'num_downloads_approx': [app_detail_ds_block, 1, 2, 13, 1],
        'num_downloads': [app_detail_ds_block, 1, 2, 13, 2],
        'published_date': [app_detail_ds_block, 1, 2, 10, 0],
        'published_timestamp': [app_detail_ds_block, 1, 2, 10, 1, 0],
        'pegi': [app_detail_ds_block, 1, 2, 9, 0],
        'pegi_detail': [app_detail_ds_block, 1, 2, 9, 2, 1],
        'os': [app_detail_ds_block, 1, 2, 140, 1, 1, 0, 0, 1],
        'rating': [app_detail_ds_block, 1, 2, 51, 0, 1],
        'description': [app_detail_ds_block, 1, 2, 72, 0, 1],
        'price': [app_detail_ds_block, 1, 2, 57, 0, 0, 0, 0, 1, 0, 2],
        'num_of_reviews': [app_detail_ds_block, 1, 2, 51, 2, 1],
        'developer_email': [app_detail_ds_block, 1, 2, 69, 1, 0],
        'developer_address': [app_detail_ds_block, 1, 2, 69, 2, 0],
        'developer_website': [app_detail_ds_block, 1, 2, 69, 0, 5, 2],
        'developer_privacy_policy_link': [app_detail_ds_block, 1, 2, 99, 0, 5, 2],
        'data_safety_list': [app_detail_ds_block, 1, 2, 136, 1],
        'updated_on': [app_detail_ds_block, 1, 2, 145, 0, 0],
        'app_version': [app_detail_ds_block, 1, 2, 140, 0, 0, 0]
    }

    @classmethod
    def get_nested_item(cls, item_holder, list_of_indexes):
        index = list_of_indexes[0]
        if len(list_of_indexes) > 1:
            return cls.get_nested_item(item_holder[index], list_of_indexes[1:])
        else:
            return item_holder[index]

    @staticmethod
    def extract_json_block(html, block_id):
        prefix = re.compile(r"AF_init[dD]ata[cC]all[bB]ack\s*\({[^{}]*key:\s*'" + re.escape(block_id) + ".*?data:")
        suffix = re.compile(r"}\s*\)\s*;")

        block = prefix.split(html)[1]
        block = suffix.split(block)[0]
        block = block.strip()
        block = re.sub(r"^function\s*\([^)]*\)\s*{", "", block)
        block = re.sub("}$", "", block)
        block = re.sub(r", sideChannel: {$", "", block)

        return block

    @classmethod
    def find_item_from_json_mapping(cls, google_app_detail_request_result, app_detail_mapping):
        ds_json_block = app_detail_mapping[0]
        json_block_raw = cls.extract_json_block(google_app_detail_request_result, ds_json_block)
        json_block = json.loads(json_block_raw)

        return cls.get_nested_item(json_block, app_detail_mapping[1:])


class MarketScraper:
    @staticmethod
    async def get_google_app_details(app_id, country="nl", lang="nl"):
        url = "https://play.google.com/store/apps/details?id={app_id}&hl={lang}&gl={country}".format(
            app_id=quote_plus(app_id),
            lang=lang,
            country=country
        )

        request_result = await async_reqget(url, 'text')

        app = {
            'id': app_id,
            'link': url,
        }

        for k, v in WebsiteMappings.app_details_mapping.items():
            app[k] = WebsiteMappings.find_item_from_json_mapping(request_result, v)

        if app.get('developer_link'):
            app['developer_link'] = f"https://play.google.com/{app['developer_link']}"

        if app.get('category'):
            app['category'] = app['category'].replace('/store/apps/category/', '')

        if app.get('data_safety_list'):
            try:
                app['data_safety_list'] = ', '.join([item[1] for item in app['data_safety_list']])
            except IndexError:
                pass

        soup = BeautifulSoup(request_result, 'html.parser')
        list_of_categories = ', '.join(
            [', '.join([category.text for category in element.find_all('span')]) for element in
             soup.find_all('div', {'class': 'Uc6QCc'})])
        if list_of_categories:
            app['list_of_categories'] = list_of_categories

        return app

    @staticmethod
    async def get_itunes_app_details(app_id, country="us", flatten=True):
        try:
            app_id = int(app_id)
            id_field = "id"
        except ValueError:
            id_field = "bundleId"

        url = "https://itunes.apple.com/lookup?%s=%s&country=%s&entity=software" % (id_field, app_id, country)

        result = await async_reqget(url, 'text')
        if result:
            result = json.loads(result)
            app = result["results"][0]

            if flatten:
                for field in app:
                    if isinstance(app[field], list):
                        app[field] = ",".join(app[field])

            return app
