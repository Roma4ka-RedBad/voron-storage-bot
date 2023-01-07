from aiogram.types import CallbackQuery, FSInputFile

from packets.base import Packet
from misc.utils import FormString
from keyboards.download import DownloadCallback


async def download_archive(cbq: CallbackQuery, server, callback_data: DownloadCallback, user_data, localization):
    await cbq.message.edit_reply_markup(None)
    message = await cbq.message.answer(FormString.paste_args(localization.DOWNLOADFILES_START,
                                                             total_files_count=0,
                                                             max_files_count=callback_data.max_files_count))
    packet = await server.send(
        Packet(13103, object_id=callback_data.object_id, message_id=message.message_id,
               language_code=user_data.language_code, compress_to_archive=True))
    await message.delete()
    if packet:
        if packet.payload.get("error_tid", None):
            return await cbq.message.answer(localization[packet.payload.error_tid])
        await cbq.message.answer_document(FSInputFile(packet.payload.result), caption=localization.PROCESS_DONE)
