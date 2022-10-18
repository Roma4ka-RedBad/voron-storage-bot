async def remove_last_new(filename: str) -> str:
    name = filename.split('/')[-1]
    ext = '.' + name.split('.')[-1]

    return name.replace('_new' + ext, ext)
