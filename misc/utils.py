import aiohttp
import os
from zipfile import ZipFile
from pathlib import Path


async def async_request(url: str, return_type: str, data=None):
    async with aiohttp.ClientSession() as session:
        if data:
            async with session.post(url, json=data) as resp:
                if resp.status == 200:
                    if return_type == 'bytes':
                        return await resp.content.read()
                    elif return_type == 'json':
                        return await resp.json()
                    elif return_type == 'text':
                        return await resp.text()
        else:
            async with session.get(url) as resp:
                if resp.status == 200:
                    if return_type == 'bytes':
                        return await resp.content.read()
                    elif return_type == 'json':
                        return await resp.json()
                    elif return_type == 'text':
                        return await resp.text()


async def compress_to_archive(archive_path: str,
                              file_paths: list = None):
    archive = ZipFile(file_writer(archive_path, b""), "w", compresslevel=10)
    if file_paths:
        for path in file_paths:
            if path:
                if os.path.isdir(path):
                    for folder, _, files in os.walk(path):
                        for _file in files:
                            arcname = os.path.join(folder.replace(path, ''), _file)
                            file_name = os.path.join(folder, _file)
                            if arcname is None:
                                arcname = Path(file_name).name
                            archive.write(filename=file_name, arcname=arcname)
                else:
                    archive.write(path)
    archive.close()
    return archive_path


def file_writer(file_name: str, data: bytes, mode: str = "wb"):
    with open(file_name, mode) as file:
        file.write(data)
        file.close()
    return file_name
