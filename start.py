import toml
import utils
import asyncio
import uvicorn
from fastapi import FastAPI
from colorama import init

from box import Box
from database import UserTable
from localization import languages
from typing import List, Dict, Any
from logic_objects import FileObject, UserObject, Metadata

from managers.game import GameManager
from managers.convert import ConvertManager

server = FastAPI()
# Для совместимости цветов с Windows
init()


@server.post("/convert/{to_format}")
async def convert(
    file: FileObject | List[FileObject],
    to_format: str,
    metadata: Dict[Any, Any] = None):
    if isinstance(file, FileObject):
        file = [file]
    for _file in file:
        _file.set_config(config)

    metadata = Metadata(metadata)
    result, content = await convert_manager.convert(file, to_format, metadata)

    if result:
        if metadata.compress_to_archive:
            paths = [obj['path'] for obj in result if obj['path']]
            if metadata.archive_only:
                result = await utils.compress_to_archive(
                    content / 'archive.zip', config, file_paths=paths)
            else:
                result = result[0] if len(result) == 1 else result
                if isinstance(result, list):
                    result = await utils.compress_to_archive(
                        content / 'archive.zip', config, file_paths=paths)

        return await utils.create_response(
            True, content={
                'result': result,
                'process_dir': content,
                })
    else:
        return await utils.create_response(False, error_msg=content)


@server.get("/localization/{language_code}")
async def get_localization(language_code: str):
    if language_code == '*':
        return await utils.create_response(True, content=languages)
    return await utils.create_response(True, content=languages[language_code])


@server.post("/user/set")
async def set_user(data: UserObject):
    user = UserTable.get(vk_id=data.vk_id, tg_id=data.tg_id)
    setattr(user, data.set_key, data.set_value)
    user.save()
    return await utils.create_response(True, content=user)


@server.post("/user/get")
async def get_user(data: UserObject):
    return await utils.create_response(
        True, content=UserTable.get_or_create(vk_id=data.vk_id, tg_id=data.tg_id)[0])


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
    content = []
    total_count = 0
    for file in files:
        file.set_config(config)
        file_converts, count_files = await utils.get_converts_by_file(file)
        total_count += count_files
        if file_converts:
            content.append(
                {
                    'path': file.path,
                    'converts': file_converts
                    })
    print(total_count)
    if total_count > 100:
        # на будущее, сделай возможность передавать максимальное кол-во файлов суда (для премиума)
        # ну и если хочешь, чтобы в error_msg была только строка, то еще и user.id, language_code и т. п.
        return await utils.create_response(
            False, error_msg={
                'tid': 'TID_TOO_MANY_FILES',
                'files_count': total_count,
                'maximum': 100
                })
    if content:
        return await utils.create_response(True, content=content)
    else:
        return await utils.create_response(False, error_msg="TID_WORK_FORMATSNOTEXIST")


async def main():
    for core in convert_manager.queue.cores:
        asyncio.create_task(core)

    asyncio.create_task(game_manager.init_prod_handler())

    # server_config = uvicorn.Config(server, host="192.168.0.127", port=80)
    server_config = uvicorn.Config(server, host='127.0.0.1', port=8910)
    a = uvicorn.Server(server_config)
    await a.serve()


if __name__ == '__main__':
    config = Box(toml.load('config.toml'))
    convert_manager = ConvertManager(config)
    game_manager = GameManager(("game.brawlstarsgame.com", 9339))
    asyncio.run(main())
