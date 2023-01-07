from aiogram.types import Message, FSInputFile
from aiogram.utils.markdown import hcode

from keyboards.download import download_kb
from packets.base import Packet
from misc.utils import FormString, get_version_and_query_by_string


async def command_download(message: Message, user_data, localization, server):
    searching_data = await get_version_and_query_by_string(message.text)
    if searching_data:
        packet = await server.send(
            Packet(13102, major_v=searching_data[1], build_v=searching_data[2], revision_v=searching_data[3],
                   search_query=searching_data[0], message_id=message.message_id, chat_id=message.chat.id,
                   platform_name="TG", metadata=user_data.metadata))
        if packet:
            if packet.payload.get("error_tid", None):
                await message.answer(FormString.paste_args(localization[packet.payload.error_tid],
                                                           name=user_data.nickname or message.from_user.first_name))
            elif packet.payload.get("file", None):
                await message.answer_document(FSInputFile(packet.payload.file),
                                              caption=FormString(localization.DOWNLOADFILES_FILES).get_form_string(
                                                  set_style="bold",
                                                  name=user_data.nickname or message.from_user.first_name,
                                                  files_count=packet.payload.files_count,
                                                  game_version=packet.payload.version
                                              ))
            elif packet.payload.get("downloaded_file", None):
                await message.answer_document(FSInputFile(packet.payload.downloaded_file),
                                              caption=FormString(localization.DOWNLOADFILES_FILE).get_form_string(
                                                  set_style="bold",
                                                  file_name=packet.payload.file_name,
                                                  game_version=packet.payload.version
                                              ))
            elif packet.payload.get("files", None):
                parts = FormString(localization.DOWNLOADFILES_BODY, split_separator="\n")
                parts = parts.get_form_string(
                    set_style="bold",
                    with_parts=True,
                    name=user_data.nickname or message.from_user.first_name,
                    files_count=packet.payload.files_count,
                    game_version=packet.payload.version,
                    files_name=''.join([f"\n  {hcode(file)}" for file in packet.payload.files])
                )

                reply_markup = None
                for part in parts:
                    if parts[-1] == part:
                        reply_markup = download_kb(localization, packet.payload.object_id, packet.payload.files_count)
                    await message.answer(part, reply_markup=reply_markup)
    else:
        await message.answer(FormString.paste_args(localization.DOWNLOADFILES_QUERY_MISSING_ERROR,
                                                   name=user_data.nickname or message.from_user.first_name))
