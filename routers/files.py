from misc import utils
from fastapi import APIRouter, Request
from typing import List

from logic_objects import FileObject, Metadata, GameData
from database import FingerprintTable

files_router = APIRouter(
    prefix="/files",
    tags=["files"]
)


@files_router.post("/convert/{to_format}")
async def convert(request: Request, file: FileObject | List[FileObject], to_format: str, metadata: Metadata = None):
    if isinstance(file, FileObject):
        file = [file]

    result, process_dir = await request.state.convert_manager.convert(file, to_format, metadata)

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


@files_router.post("/searching")
async def search_files(request: Request, game_data: GameData):
    fingerprint = FingerprintTable.get_or_none(FingerprintTable.major_v == game_data.major_v,
                                               FingerprintTable.build_v == game_data.build_v,
                                               FingerprintTable.revision_v == game_data.revision_v)
    if not fingerprint:
        fingerprint = FingerprintTable.get(FingerprintTable.is_actual)

    content = {
        'files': await request.state.game_manager.search_files(game_data.search_query, fingerprint.sha),
        'version': f"{fingerprint.major_v}.{fingerprint.build_v}.{fingerprint.revision_v}"
    }
    if not content['files']:
        return await utils.create_response(False, error_msg="TID_DOWNLOADFILES_NOTFOUND")
    else:
        return await utils.create_response(True, content=content)


@files_router.post("/downloading")
async def download_files(request: Request, game_data: GameData, metadata: Metadata = None):
    fingerprint = FingerprintTable.get_or_none(FingerprintTable.major_v == game_data.major_v,
                                               FingerprintTable.build_v == game_data.build_v,
                                               FingerprintTable.revision_v == game_data.revision_v)
    if not fingerprint:
        fingerprint = FingerprintTable.get(FingerprintTable.is_actual)
    files = await request.state.game_manager.search_files(game_data.search_query, fingerprint.sha)
    result = []
    for file in files:
        result.append(await request.state.game_manager.download_file(fingerprint.sha, file, result_path=game_data.path))

    if metadata.compress_to_archive:
        result = await utils.compress_to_archive(game_data.path / 'archive.zip', file_paths=result)

    return await utils.create_response(True, content=result)


@files_router.post("/counting")
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


@files_router.post("/converts")
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
