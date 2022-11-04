import aiohttp
from box import Box

from asyncio.exceptions import TimeoutError
from aiohttp.client_exceptions import ContentTypeError


class Server:
    def __init__(self, address: str):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=0))
        self.address = address
        self.messenger = 'VK'
        self.timezone = None

    async def send_message(self, endpoint: str, **kwargs):
        try:
            use_method = self.session.get(f'{self.address}/{endpoint}') if not kwargs \
                else self.session.post(f'{self.address}/{endpoint}', json=kwargs)

            async with use_method as request:
                response = await request.json()
                response = Box(response)
        except (TimeoutError, ContentTypeError):
            response = None

        print(response, endpoint)
        return response

    async def close(self):
        await self.session.close()
