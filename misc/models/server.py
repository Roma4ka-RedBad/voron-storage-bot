import aiohttp
from box import Box


class Server:
    def __init__(self, address: str):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=0))
        self.address = address
        self.messenger = 'TG'
        self.timezone = None

    async def send_msg(self, endpoint: str, *args, **kwargs):
        if args:
            args = args[0]

        try:
            use_method = self.session.get(f'{self.address}/{endpoint}') if not args and not kwargs \
                else self.session.post(f'{self.address}/{endpoint}', json=args or kwargs)

            async with use_method as request:
                response = await request.json()
                response = Box(response)
        except:
            response = None

        return response

    async def close(self):
        await self.session.close()
