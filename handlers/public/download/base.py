import re
from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server
from misc.utils import safe_split_text


async def command_download(message: Message, server: Server, user_localization):
    if not user_localization:
        return await message.answer(text='Подключение к серверу отсутствует!')

    raw_text = message.text.split()
    raw_text.pop(0)
    if raw_text:
        version = re.search("\d+[\.]\d+([\.]\d+)?", ''.join(raw_text))
        version = version[0] if version else None
        major_v, build_v, revision_v = None, None, 1
        if version:
            for x in raw_text:
                if version in x:
                    raw_text.remove(x)
            version = version.split('.')
            major_v = version[0]
            build_v = version[1]
            revision_v = version[2] if len(version) > 2 else 1

        searching_files = await server.send_msg("search_files", search_query=''.join(raw_text), major_v=major_v,
                                                build_v=build_v, revision_v=revision_v)
        if searching_files.status:
            parts = await safe_split_text(user_localization.TID_DOWNLOADFILES_TEXT.format(
                files_count=len(searching_files.content.files),
                game_version=searching_files.content.version,
                files_name=''.join([f"\n  {hcode(file)}" for file in searching_files.content.files])
            ), split_separator='\n')
            for part in parts:
                await message.answer(hbold(part).replace('&lt;', '<').replace('&gt;', '>'))
        else:
            await message.answer(user_localization[searching_files.error_msg])
    else:
        await message.answer(user_localization.TID_DOWNLOADFILES_QUERYMISSING)
