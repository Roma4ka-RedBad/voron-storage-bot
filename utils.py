from logic_objects import FileObject, ArchiveObject
from typing import List
import os


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
            return archive_converts
    else:
        return file.get_available_converts()


async def compress_to_archive(archive_path: str, config: object,
                              files_objects: List[FileObject] = None,
                              file_paths: list = None):
    archive = ArchiveObject(FileObject.create(archive_path, config), "w", "zip", compresslevel=10)

    if files_objects:
        for file in files_objects:
            archive.write(file.path)

    if file_paths:
        for path in file_paths:
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


async def create_response(status: bool, content=None, error_msg: str = None):
    response = {
        "status": status
    }

    if status:
        response['content'] = content
    else:
        response['error_msg'] = error_msg

    return response
