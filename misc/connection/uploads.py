from vkbottle import API, Bot, DocMessagesUploader
from vkbottle_types.objects import MessagesForward
from typing import Tuple, List, Optional
from aiohttp import ClientSession
from pathlib import Path
from random import randint


def get_valid_link(response):
    doc = response.doc
    owner = doc.owner_id
    doc_id = doc.id
    access_key = doc.access_key
    return f'doc{owner}_{doc_id}{("_" + access_key) if access_key else ""}'


async def upload(docs: List[Path], user_api: API, bot: Bot,
                 localization, peer_id, rename: bool = False
                 ) -> Tuple[List[str],bool]:
    have_big_file = any(file.stat().st_size > 220 * 1024 * 1024 for file in docs)
    files = []
    if have_big_file:
        server = await user_api.docs.get_upload_server()
        api = user_api
    else:
        server = await bot.api.docs.get_messages_upload_server(type='doc', peer_id=peer_id)
        api = bot.api

    async with ClientSession() as session:
        for filepath in docs:
            if rename and filepath.suffix == '.zip':
                filepath = filepath.rename(str(filepath) + '1')
            name = filepath.name
            async with session.post(server.upload_url,
                                    data={'file': filepath.open('rb')}) as request:
                response = await request.json()
                dump = await api.docs.save(file=response['file'], title=name)
                files.append(get_valid_link(dump))

    if not files:
        return files, have_big_file

    if have_big_file:
        text = localization.TID_FILES_LOADED_VIA_USERAPI if len(files) > 1 else localization.TID_FILE_LOADED_VIA_USERAPI
        message = await user_api.messages.get_by_id([
            await user_api.messages.send(
                message=text,
                attachment=files or None,
                user_id=-198411230,
                random_id=randint(1, 2345678))])

        result = MessagesForward(peer_id=470988909,
                                 conversation_message_ids=[message.items[0].conversation_message_id]).json()
    else:
        result = files

    return result, have_big_file
