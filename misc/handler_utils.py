def commands_to_regex(*args: str) -> str:
    args = [arg.lower() for arg in args]
    group_id = 198411230
    prefixes = ['/', '!']

    mention = f'\\[club{group_id}\\|.*\\] *'
    prefixes = '|'.join([f'({prefix})' for prefix in prefixes])
    start = f'(({mention})|' + prefixes + ')'
    command = '|'.join(args)

    return f'{start}({command})'


async def get_nickname(userdata, api, clickable=False):
    nickname = userdata.nickname
    if userdata.nickname is None:
        nickname = (await api.users.get(user_ids=[userdata.vk_id]))[0].first_name

    if clickable:
        nickname = f'[id{userdata.vk_id}|{nickname}]'

    return nickname
