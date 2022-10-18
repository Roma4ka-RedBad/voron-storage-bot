import aiohttp
from box import Box


class Server:
    def __init__(self, address: str):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=0))
        self.address = address
        self.messenger = 'VK'
        self.timezone = None

    async def send_message(self, endpoint: str, data: dict | list = None):
        try:
            use_method = self.session.get(f'{self.address}/{endpoint}') if not data \
                else self.session.post(f'{self.address}/{endpoint}', json=data)

            async with use_method as request:
                response = await request.json()
                response = Box(response)
        finally:
            response = None

        return response

    async def close(self):
        await self.session.close()