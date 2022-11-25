import utils
import asyncio
import uvicorn
from fastapi import FastAPI
import colorama

from database import UserTable, FingerprintTable
from localization import languages
from typing import List
from logic_objects import FileObject, UserObject, Metadata, GameData, Config

from managers.game import GameManager
from managers.convert import ConvertManager
from managers.messengers import MessengersManager

server = FastAPI()


@server.post("/convert/{to_format}")
async def convert(file: FileObject | List[FileObject], to_format: str, metadata: Metadata = None):
    if isinstance(file, FileObject):
        file = [file]

    result, process_dir = await convert_manager.convert(file, to_format, metadata)

    if result is None and process_dir is None:
        return await utils.create_response(False, content={
            'result': [],
            'process_dir': '',
        }, error_msg='TID_STARTWORK_FILENOTFOUND')

    response_code = True
    error_msg = None

    if metadata.compress_to_archive:
        paths = [obj['path'] for obj in result if obj['path']]
        if metadata.archive_only:
            result = await utils.compress_to_archive(process_dir / 'archive.zip', file_paths=paths)
        else:
            if len(paths) > 1:
                result = await utils.compress_to_archive(process_dir / 'archive.zip', file_paths=paths)
                result = [{'path': result, 'tid': None}]

    if metadata.return_one_file:
        result = result[0]
        if not result['path']:
            response_code = False
            error_msg = result['tid']

    return await utils.create_response(response_code, content={
        'result': result,
        'process_dir': process_dir,
    }, error_msg=error_msg)


@server.post("/search_files")
async def search_files(game_data: GameData):
    fingerprint = FingerprintTable.get_or_none(FingerprintTable.major_v == game_data.major_v,
                                               FingerprintTable.build_v == game_data.build_v,
                                               FingerprintTable.revision_v == game_data.revision_v)
    if not fingerprint:
        fingerprint = FingerprintTable.get(FingerprintTable.is_actual)

    content = {
        'files': await game_manager.search_files(game_data.search_query, fingerprint.sha),
        'version': f"{fingerprint.major_v}.{fingerprint.build_v}.{fingerprint.revision_v}"
    }
    if not content['files']:
        return await utils.create_response(False, error_msg="TID_DOWNLOADFILES_NOTFOUND")
    else:
        return await utils.create_response(True, content=content)


@server.post("/download_files")
async def download_files(game_data: GameData, metadata: Metadata = None):
    fingerprint = FingerprintTable.get_or_none(FingerprintTable.major_v == game_data.major_v,
                                               FingerprintTable.build_v == game_data.build_v,
                                               FingerprintTable.revision_v == game_data.revision_v)
    if not fingerprint:
        fingerprint = FingerprintTable.get(FingerprintTable.is_actual)
    files = await game_manager.search_files(game_data.search_query, fingerprint.sha)
    result = []
    for file in files:
        result.append(await game_manager.download_file(fingerprint.sha, file, result_path=game_data.path))

    if metadata.compress_to_archive:
        result = await utils.compress_to_archive(game_data.path / 'archive.zip', file_paths=result)

    return await utils.create_response(True, content=result)


@server.get("/localization/{language_code}")
async def get_localization(language_code: str):
    if language_code == '*':
        return await utils.create_response(True, content=languages)
    return await utils.create_response(True, content=languages[language_code])


@server.post("/user/set")
async def set_user(data: UserObject):
    user = None
    if data.vk_id:
        user = UserTable.get(vk_id=data.vk_id)
    elif data.tg_id:
        user = UserTable.get(tg_id=data.tg_id)

    if '.' not in data.set_key:
        setattr(user, data.set_key, data.set_value)
        user.save()
    else:
        user_object = getattr(user, data.set_key.split('.')[0])
        setattr(user_object, data.set_key.split('.')[-1], data.set_value)
        user_object.save()

    user.__data__['metadata'] = user.metadata.__data__
    return await utils.create_response(True, content=user.__data__)


@server.get("/markets/{language_code}")
async def get_markets(language_code: str):
    content = {
        1: await game_manager.get_market_data(1, language_code),
        2: await game_manager.get_market_data(2, language_code)
    }

    return await utils.create_response(True, content=content)


@server.get("/fingerprints")
async def get_fingerprints():
    actual_finger = FingerprintTable.get(FingerprintTable.is_actual)
    new_finger = await game_manager.server_data(actual_finger.major_v, actual_finger.build_v, actual_finger.revision_v)
    old_finger = FingerprintTable.get_or_none(FingerprintTable.id == (actual_finger.id - 1))
    content = {
        'actual_finger': actual_finger.__data__,
        'new_finger': new_finger,
        'old_finger': old_finger.__data__ if old_finger else None,
        'fingerprints': [finger.__data__ for finger in
                         FingerprintTable.select().order_by(-FingerprintTable.major_v,
                                                            -FingerprintTable.build_v).execute()],
    }

    return await utils.create_response(True, content=content)


@server.post("/user/get")
async def get_user(data: UserObject):
    user = None
    if data.vk_id is not None:
        user = UserTable.get_or_create(vk_id=data.vk_id)
    elif data.tg_id is not None:
        user = UserTable.get_or_create(tg_id=data.tg_id)

    user[0].__data__['metadata'] = user[0].metadata.__data__
    return await utils.create_response(True, content=user[0].__data__)


@server.get("/config")
async def get_config():
    return await utils.create_response(True, content=Config)


@server.post("/check_count")
async def check_count(files: List[FileObject], metadata: Metadata):
    response_code = True
    error_msg = None

    result = {
        'files_count': 0,
        'maximum_count': metadata.files_count_limit
    }

    for file in files:
        if archive := file.get_archive():
            result['files_count'] += archive.count()
        else:
            result['files_count'] += 1

    if result['files_count'] > result['maximum_count']:
        response_code = False
        error_msg = "TID_TOO_MANY_FILES"

    return await utils.create_response(response_code, content=result, error_msg=error_msg)


@server.post("/converts")
async def get_converts(files: List[FileObject]):
    content = []
    for file in files:
        file_converts = await utils.get_converts_by_file(file)
        if file_converts:
            content.append({
                'path': file.path,
                'converts': file_converts
            })
    if content:
        return await utils.create_response(True, content=content)
    else:
        return await utils.create_response(False, error_msg="TID_WORK_FORMATSNOTEXIST")


async def main():
    for core in convert_manager.queue.cores:
        asyncio.create_task(core)

    await game_manager._init()
    game_tasks = set()
    game_tasks.add(asyncio.create_task(game_manager.init_prod_handler()))

    server_config = uvicorn.Config(server, host='127.0.0.1', port=8910, use_colors=True, access_log=True)
    a = uvicorn.Server(server_config)
    await a.serve()


if __name__ == '__main__':
    convert_manager = ConvertManager()
    messengers_manager = MessengersManager()
    game_manager = GameManager(("game.brawlstarsgame.com", 9339))

    colorama.init()
    asyncio.run(main())
