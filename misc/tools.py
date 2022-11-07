import shutil
from vkbottle import Bot

from misc.models.storage import FileStorage


def remove_dir_and_file(storage: FileStorage, message_id: int, user_id: int, config, server):
        path = f"{config.UFS.path}VK/{user_id}/{message_id}"
        storage.delete(user_id, message_id)
        shutil.rmtree(path, ignore_errors=True)


