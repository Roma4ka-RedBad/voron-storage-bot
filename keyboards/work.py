from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from misc.models import DownloadedFile


class WorkCallback(CallbackData, prefix="work"):
    action: str
    to_format: str = None
    condition: bool = None
    is_archive: bool = False
    row_index: int = 0


async def construct_convert_buttons(converts, row_index, is_archive=False):
    buttons = []
    for convert in converts:
        callback_data = WorkCallback(action='convert', row_index=row_index, to_format=convert, is_archive=is_archive)
        buttons.append(InlineKeyboardButton(text=convert, callback_data=callback_data.pack()))
    return buttons


def work_keyb(localization):
    kb_obj = InlineKeyboardBuilder()
    kb_obj.row(InlineKeyboardButton(text=localization.TID_BUTTON_ARCHIVE_ALL,
                                    callback_data=WorkCallback(action='by_archive', condition=True).pack()))
    kb_obj.row(InlineKeyboardButton(text=localization.TID_BUTTON_ARCHIVE_FILE,
                                    callback_data=WorkCallback(action='by_archive', condition=False).pack()))

    return kb_obj.as_markup()


async def work_converts_keyb(file_converts, file: DownloadedFile, condition: bool = None):
    kb_obj = InlineKeyboardBuilder()

    if file.is_archive() and not condition:
        row_index = 0
        for archive_file in file_converts.converts.archive_files:
            convert_buttons = await construct_convert_buttons(archive_file.converts, row_index, True)
            kb_obj.row(InlineKeyboardButton(
                text=archive_file.short_name,
                callback_data=WorkCallback(action='show_filename', row_index=row_index).pack()
            ), *convert_buttons)
            row_index += 1
    else:
        convert_buttons = await construct_convert_buttons(
            file_converts.converts.archive_converts if file.is_archive() else file_converts.converts, 0, file.is_archive())
        kb_obj.row(InlineKeyboardButton(text=file.name,
                                        callback_data=WorkCallback(action='show_filename').pack()
                                        ), *convert_buttons, width=6)

    return kb_obj.as_markup()
