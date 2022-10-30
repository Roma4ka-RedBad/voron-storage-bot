from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from misc.models import DownloadedFile


class WorkCallback(CallbackData, prefix="work"):
    action: str
    to_format: str = None
    file_id: int = None
    subfile_id: int = None
    row_index: int = None
    by_archive: bool = None


async def construct_convert_buttons(converts, file_id: int, subfile_id: int = None):
    buttons = []
    for convert in converts:
        callback_data = WorkCallback(action='convert', to_format=convert, file_id=file_id, subfile_id=subfile_id)
        buttons.append(InlineKeyboardButton(text=convert, callback_data=callback_data.pack()))
    return buttons


def work_keyb(localization, file_id: int):
    kb_obj = InlineKeyboardBuilder()
    kb_obj.row(InlineKeyboardButton(text=localization.TID_BUTTON_ARCHIVE_ALL,
                                    callback_data=WorkCallback(action='by_archive', by_archive=False,
                                                               file_id=file_id).pack()))
    kb_obj.row(InlineKeyboardButton(text=localization.TID_BUTTON_ARCHIVE_FILE,
                                    callback_data=WorkCallback(action='by_archive', by_archive=True,
                                                               file_id=file_id).pack()))

    return kb_obj.as_markup()


async def work_converts_keyb(file_converts, file: DownloadedFile, file_id: int, by_archive: bool = False):
    kb_obj = InlineKeyboardBuilder()

    if file.is_archive() and by_archive:
        row_index = 0
        for archive_file in file_converts.converts.archive_files:
            convert_buttons = await construct_convert_buttons(archive_file.converts, file_id,
                                                               file.get_index_by_target_filename(archive_file.name))
            kb_obj.row(InlineKeyboardButton(
                text=archive_file.short_name,
                callback_data=WorkCallback(action='show_filename', row_index=row_index).pack()
            ), *convert_buttons)
            row_index += 1
    else:
        convert_buttons = await construct_convert_buttons(
            file_converts.converts.archive_converts if file.is_archive() else file_converts.converts, file_id)
        kb_obj.row(*convert_buttons, width=6)

    return kb_obj.as_markup()
