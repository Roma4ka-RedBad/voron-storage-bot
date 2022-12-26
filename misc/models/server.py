import aiohttp
import logging
from box import Box


class Server:
    def __init__(self, address: str):
        self.address = address
        self.messenger = 'TG'
        self.timezone = None

    @staticmethod
    async def request(url: str, timeout: int, return_type: str = 'box', data = None):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
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
                        logging.error(await resp.text())
            else:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        if return_type == 'box':
                            return Box(await resp.json())
                        elif return_type == 'json':
                            return await resp.json()
                        elif return_type == 'text':
                            return await resp.text()

    async def send_msg(self, endpoint: str, *args, **kwargs):
        try:
            if args:
                args = args[0]
            timeout = 5*60
            if 'timeout' in kwargs:
                timeout = kwargs['timeout']
                kwargs.pop('timeout')
            data = await self.request(f'{self.address}/{endpoint}', timeout, data=args or kwargs)
        except:
            data = None

        return data
