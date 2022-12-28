import aiohttp
from box import Box


class Server:
    def __init__(self, address: str):
        self.address = address
        self.messenger = 'VK'
        self.timezone = None

    async def request(self, url: str, return_type: str = 'box', data=None):
        async with aiohttp.ClientSession() as session:
            if data:
                async with session.post(url, json=data) as resp:
                    if resp.status == 200:
                        if return_type == 'box':
                            return Box(await resp.json())
                        elif return_type == 'json':
                            return await resp.json()
                        elif return_type == 'text':
                            return await resp.text()
            else:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        if return_type == 'box':
                            return Box(await resp.json())
                        elif return_type == 'json':
                            return await resp.json()
                        elif return_type == 'text':
                            return await resp.text()

    async def send_message(self, endpoint: str, *args, **kwargs):
        try:
            if args:
                args = args[0]
            data = await self.request(f'{self.address}/{endpoint}', data=args or kwargs)

        except None:
            data = None

        return data

