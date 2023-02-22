from aiohttp import ClientSession
from misc.models import FileModel
from pathlib import Path


async def download_raw_file(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            a = await response.read()

    return a


async def download_and_save_file(session: ClientSession, url: str, path: str | Path):
    async with session.get(url) as resp:
        with open(path, 'wb') as file:
            async for chunk in resp.content.iter_chunked(1024 * 1024 * 10):
                file.write(chunk)


async def get_files(file_objects: list[FileModel] | FileModel, path: str | Path) -> int:
    if isinstance(file_objects, FileModel):
        file_objects = [file_objects]

    file_models = []
    async with ClientSession() as session:
        for file_object in file_objects:
            if file_object.url:
                file = await download_and_save_file(session, file_object.url, path / file_object.name)
                file_models.append(file)

    return len(file_models)
