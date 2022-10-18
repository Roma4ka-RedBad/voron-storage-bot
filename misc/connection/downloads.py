from aiohttp import ClientSession
from misc.models.downloadable_file import File
from misc.models.prepared_file import DownloadedFile


async def download_and_save_file(session: ClientSession, file_object: File) -> DownloadedFile:
    path = f'{file_object.main_dir}/{file_object.user_dir}/{file_object.name}'
    async with session.get(file_object.url) as resp:
        with open(path, 'wb') as file:
            async for chunk in resp.content.iter_chunked(1024*1024*10):
                file.write(chunk)

    return DownloadedFile(file_object.main_dir, file_object.user_dir, file_object.name)


async def get_files(file_objects: list[File, ...] | File) -> list[DownloadedFile, ...]:
    if isinstance(file_objects, File):
        file_objects = [file_objects]

    file_models = []
    async with ClientSession() as session:
        for file_object in file_objects:
            file = await download_and_save_file(session, file_object)
            file_models.append(file)

    return file_models
