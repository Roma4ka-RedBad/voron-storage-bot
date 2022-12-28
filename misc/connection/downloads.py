from aiohttp import ClientSession

from misc.models import DownloadedFile
from misc.models import FileModel


async def download_and_save_file(session: ClientSession, file_object: FileModel) -> DownloadedFile:
    path = f'{file_object.main_dir}/{file_object.user_dir}/{file_object.name}'
    async with session.get(file_object.url) as resp:
        with open(path, 'wb') as file:
            async for chunk in resp.content.iter_chunked(1024 * 1024 * 10):
                file.write(chunk)

    return DownloadedFile(file_object.main_dir, file_object.user_dir, file_object.name)


async def get_files(file_objects: list[FileModel] | FileModel) -> list[DownloadedFile]:
    if isinstance(file_objects, FileModel):
        file_objects = [file_objects]

    file_models = []
    async with ClientSession() as session:
        for file_object in file_objects:
            if file_object.url:
                file = await download_and_save_file(session, file_object)
                file_models.append(file)

    return file_models


async def download_raw_file(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            a = await response.read()

    return a
