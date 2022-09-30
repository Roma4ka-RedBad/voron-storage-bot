from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from misc.file import DownloadedFile


class WorkCallback(CallbackData, prefix="work"):
    action: str
    to_format: str = None
    row_index: int = 0


async def construct_convert_buttons(converts, row_index):
    buttons = []
    for convert in converts.converts:
        callback_data = WorkCallback(action='convert', row_index=row_index, to_format=convert)
        buttons.append(InlineKeyboardButton(text=convert, callback_data=callback_data.pack()))
    return buttons


async def work_keyb(converts, file: DownloadedFile):
    kb_obj = InlineKeyboardBuilder()

    if file.is_archive():
        row_index = 0
        for archive_file in converts.converts:
            convert_buttons = await construct_convert_buttons(archive_file, row_index)
            kb_obj.row(InlineKeyboardButton(
                text=archive_file.short_name,
                callback_data=WorkCallback(action='show_filename', row_index=row_index).pack()
            ), *convert_buttons)
            row_index += 1
    else:
        convert_buttons = await construct_convert_buttons(converts, 0)
        kb_obj.row(InlineKeyboardButton(text=file.name,
                                        callback_data=WorkCallback(action='show_filename').pack()
                                        ), *convert_buttons)

    return kb_obj.as_markup()
