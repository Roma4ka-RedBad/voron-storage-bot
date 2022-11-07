import shutil
from misc.models.storage import FileStorage


async def remove_dir_and_file(storage: FileStorage, message_id: int, user_id: int, config):
        # просто чтобы знать, что функция сработала
        print(user_id, message_id)
        path = f"{config.UFS.path}VK/{user_id}/{message_id}"
        storage.delete(user_id, message_id)
        shutil.rmtree(path, ignore_errors=True)


