from box import Box
from asyncio.exceptions import TimeoutError
from aiohttp.client_exceptions import ContentTypeError
from aiohttp import ClientSession, ClientTimeout


class Server:
    def __init__(self, address: str):
        self.session = ClientSession(timeout=ClientTimeout(total=0))
        self.address = address
        self.messenger = 'VK'
        self.timezone = None

    async def send_message(self, endpoint: str, *args, **kwargs) -> None | Box:
        if args:
            args = args[0]

        try:
            use_method = self.session.get(f'{self.address}/{endpoint}') if not args and not kwargs \
                else self.session.post(f'{self.address}/{endpoint}', json=args or kwargs)

            async with use_method as request:
                response = await request.json()
                response = Box(response)
        except (ContentTypeError, TimeoutError):
            response = None

        return response

    async def close(self):
        await self.session.close()
