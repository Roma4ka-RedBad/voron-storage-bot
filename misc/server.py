import aiohttp
from box import Box


class Server:
    def __init__(self, address: str):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=0))
        self.address = address

    async def send_message(self, endpoint: str, data: dict | list = None):
        if data:
            async with self.session.post(f'{self.address}/{endpoint}', json=data) as request:
                response = await request.json()
                response = Box(response['content'])
        else:
            async with self.session.get(f'{self.address}/{endpoint}') as request:
                response = await request.json()
                response = Box(response['content'])

        return response
