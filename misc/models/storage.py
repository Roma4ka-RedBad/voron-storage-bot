from typing import List, Tuple


class FileStorage:
    def __init__(self):
        self.storage = {}
        self.active_converts = []

    def put(self, user_id, message_id, file_converts, buttons: List[List[str] | Tuple[str] | str] = None):
        temp = {}
        ID = f'{user_id}_{message_id}'
        for item in file_converts:
            if 'archive_converts' in item.converts:
                temp[item.path] = item.converts.archive_converts
            else:
                temp[item.path] = item.converts

        if buttons is None:
            buttons = []
            for item in file_converts:
                if 'archive_converts' in item.converts:
                    buttons.append(item.converts.archive_converts)
                else:
                    buttons.append(item.converts)

        self.storage[ID] = {'converts': temp, 'buttons': buttons}
        return ID

    def get(self, user_id, message_id):
        try:
            return self.storage[f'{user_id}_{message_id}']
        except KeyError:
            return None

    def get_files(self, user_id, message_id) -> List:
        try:
            return self.storage[f'{user_id}_{message_id}']['converts']
        except KeyError:
            return []

    def get_converts(self, user_id, message_id) -> List:
        try:
            return self.storage[f'{user_id}_{message_id}']['buttons']
        except KeyError:
            return []

    def delete(self, user_id: int, message_id: int):
        try:
            self.storage.pop(f'{user_id}_{message_id}')
        except KeyError:
            pass
