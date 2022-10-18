def commands_to_regex(*args) -> str:
    group_id = 198411230
    prefixes = ['/', '!']

    mention = f'\\[club{group_id}\\|.*\\] *'
    prefixes = '|'.join([f'({prefix})' for prefix in prefixes])
    start = f'(({mention})|' + prefixes + ')'
    command = '|'.join(args)

    print(f'{start}({command})')
    return f'{start}({command})'
