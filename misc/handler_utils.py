import re


def commands_to_regex(*args: str, exactly: bool = False) -> str:
    # Только с префиксами! Это было сделано для поддержки команд в беседах
    args = [arg.lower() for arg in args]
    group_id = 198411230
    prefixes = ['/', '!']

    mention = f'\\[club{group_id}\\|.*\\] *'
    prefixes = '|'.join([f'({prefix})' for prefix in prefixes])
    start = f'(({mention})|' + prefixes + ')'
    command = '|'.join(args)

    return f'{start}({command})\b' if exactly else f'{start}({command})'


async def get_nickname(userdata, api, clickable=False):
    nickname = userdata.nickname
    if userdata.nickname is None or userdata.nickname == '':
        nickname = (await api.users.get(user_ids=[userdata.vk_id]))[0].first_name

    if clickable:
        nickname = f'[id{userdata.vk_id}|{nickname}]'

    return nickname


class Regex:
    def __init__(self, text):
        self.text = text
        self.split_text = None

    def split(self, pattern):
        result = re.split(pattern, self.text)
        for i in range(result.count('')):
            result.remove('')
        self.split_text = result

        return result

    def search(self, pattern):
        return re.search(pattern, self.text)
