from aiohttp import ClientSession


async def download_raw_file(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            a = await response.read()

    return a
