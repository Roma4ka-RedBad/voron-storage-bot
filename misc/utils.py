import aiohttp


async def async_request(url: str, return_type: str, data=None):
    async with aiohttp.ClientSession() as session:
        if data:
            async with session.post(url, json=data) as resp:
                if resp.status == 200:
                    if return_type == 'bytes':
                        return await resp.content.read()
                    elif return_type == 'json':
                        return await resp.json()
                    elif return_type == 'text':
                        return await resp.text()
        else:
            async with session.get(url) as resp:
                if resp.status == 200:
                    if return_type == 'bytes':
                        return await resp.content.read()
                    elif return_type == 'json':
                        return await resp.json()
                    elif return_type == 'text':
                        return await resp.text()


def file_writer(file_name: str, data: bytes):
    with open(file_name, "wb") as file:
        file.write(data)
        file.close()
    return file_name
