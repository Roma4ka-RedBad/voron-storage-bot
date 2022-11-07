from logic_objects import FileObject, ArchiveObject
from typing import List
import os
import aiohttp


async def get_converts_by_file(file: FileObject):
    if archive := file.get_archive():
        archive_converts = {
            "archive_files": [
                {
                    "name": file.origin.filename,
                    "short_name": file.get_shortname(),
                    "converts": file.get_available_converts()
                }
                for file in archive.get_files() if file.get_available_converts()
            ],
            "archive_converts": archive.get_available_converts()
        }

        if len(archive_converts['archive_files']):
            return archive_converts, len(archive_converts['archive_files'])
    else:
        return file.get_available_converts(), 1


async def compress_to_archive(archive_path: str, config: object,
                              files_objects: List[FileObject] = None,
                              file_paths: list = None):
    archive = ArchiveObject(FileObject.create(archive_path, config), "w", "zip", compresslevel=10)

    if files_objects:
        for file in files_objects:
            archive.write(file.path)

    if file_paths:
        for path in file_paths:
            if path:
                if os.path.isdir(path):
                    for folder, _, files in os.walk(path):
                        for _file in files:
                            archive.write(
                                os.path.join(folder, _file),
                                arc_name=os.path.join(folder.replace(path, ''), _file)
                            )
                else:
                    archive.write(path)

    return archive.close()


async def async_reqget(url: str, return_type: str, headers: dict = None):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if return_type == 'text':
                return await resp.text()

            if return_type == 'json':
                return await resp.json()


async def create_response(status: bool, content=None, error_msg: str | dict = None):
    response = {
        "status": status
    }

    if content:
        response['content'] = content

    if error_msg:
        response['error_msg'] = error_msg

    return response
