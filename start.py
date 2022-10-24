import uvicorn
import utils
import toml

from fastapi import FastAPI
from typing import List, Dict, Any
from box import Box

from logic_objects import FileObject, UserObject
from convert.manager import ConvertManager
from localization import languages
from database import UserTable

config = Box(toml.load('config.toml'))
manager = ConvertManager(config)
server = FastAPI()


@server.post("/convert/{to_format}")
async def convert(file: FileObject, to_format: str, metadata: Dict[Any, Any] = None):
    file.set_config(config)
    result, process_dir = await manager.convert(file, to_format, metadata)
    if result:
        return await utils.create_response(True, content={
            'result_file': result,
            'process_dir': process_dir,
        })
    else:
        return await utils.create_response(False)


@server.get("/localization/{language_code}")
async def get_localization(language_code: str):
    return await utils.create_response(True, content=languages[language_code])


@server.get("/localizations")
async def get_localizations():
    return await utils.create_response(True, content=languages)


@server.post("/user/set")
async def set_user(data: UserObject):
    user = UserTable.get(vk_id=data.vk_id, tg_id=data.tg_id)
    setattr(user, data.set_key, data.set_value)
    user.save()
    return await utils.create_response(True, content=user)


@server.post("/user/get")
async def get_user(data: UserObject):
    return await utils.create_response(True, content=UserTable.get_or_create(vk_id=data.vk_id, tg_id=data.tg_id)[0])


@server.get("/config")
async def get_config():
    return await utils.create_response(True, content=config)


@server.get("/limit/{file_format}")
async def get_limit(file_format: str):
    if file_format in config.FILE_SIZE_LIMITS:
        result = config.FILE_SIZE_LIMITS[file_format]
    else:
        result = config.FILE_SIZE_LIMITS.default

    return await utils.create_response(True, content=result * 1024 * 1024)


@server.post("/converts")
async def get_converts(files: List[FileObject]):
    if len(files) > 1:
        content = []
        for file in files:
            file.set_config(config)
            file_converts = await utils.get_converts_by_file(file)
            if file_converts:
                content.append({
                    'path': file.path,
                    'converts': file_converts
                })
        return await utils.create_response(True, content=content)

    else:
        files[0].set_config(config)
        file_converts = await utils.get_converts_by_file(files[0])
        if file_converts:
            return await utils.create_response(True, content={
                'path': files[0].path,
                'converts': file_converts
            })

        return await utils.create_response(False,
                                           error_msg="TID_WORK_FORMATSNOTEXIST")


# Принимает словарь, где path: путь до папки, которую надо архивировать
# Путь без конечного слеша
@server.post("/to_archive")
async def compress_folder(data: dict):
    final_path = await manager.compress_to_archive(**data)
    return await utils.create_response(
            True, content={
                'archive_path': final_path
                })


# uvicorn.run(server, host="192.168.0.127", port=80)
uvicorn.run(server, host='127.0.0.1', port=8910)
