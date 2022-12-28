import shutil
from asyncio import sleep

from loguru import logger

from misc.models.storage import FileStorage


async def remove_dir_and_file(storage: FileStorage, message_id: int, user_id: int, config):
    path = f"{config.UFS.path}VK/{user_id}/{message_id}"
    storage.delete(user_id, message_id)
    deleted = False
    while not deleted:
        try:
            shutil.rmtree(path, ignore_errors=False)
            deleted = True

        except PermissionError:
            logger.warning(f'Permission denied with "VK/{user_id}/{message_id}"')
            await sleep(1)

        except (FileExistsError, FileNotFoundError):
            logger.info(f'Folder has already deleted "VK/{user_id}/{message_id}"')
            return

    logger.info(f'Folder has deleted "VK/{user_id}/{message_id}"')
