import os

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from misc.file import DownloadedFile


class WorkCallback(CallbackData, prefix="work"):
    action: str
    file_index: str = None
    to_format: str = None
    row_index: int = 0


async def work_keyb(buttons: dict, file: DownloadedFile):
    kb_obj = InlineKeyboardBuilder()

    for file_name in buttons:
        if not file.is_archive():
            format_buttons = None
            if len(buttons[file_name]) > 0:
                format_buttons = [InlineKeyboardButton(text=file_format, callback_data=WorkCallback(action='working',
                                                                                                    file_index=file.get_index(),
                                                                                                    to_format=file_format).pack())
                                  for file_format in buttons[file_name]]

            if not format_buttons:
                return None

            kb_obj.row(InlineKeyboardButton(
                text=file_name.split('/')[-1],
                callback_data=WorkCallback(action='show_filename').pack()
            ), *format_buttons)
        else:
            row_index = 0
            for file_in_arch_name in buttons[file_name]:
                format_buttons = []
                if len(buttons[file_name][file_in_arch_name]) > 0:
                    format_buttons = [
                        InlineKeyboardButton(text=file_format, callback_data=WorkCallback(action='working',
                                                                                          file_index=file.get_index(),
                                                                                          to_format=file_format).pack())
                        for file_format in buttons[file_name][file_in_arch_name]]

                if format_buttons:
                    kb_obj.row(InlineKeyboardButton(
                        text=file_in_arch_name.split('/')[-1],
                        callback_data=WorkCallback(action='show_filename', row_index=row_index).pack()
                    ), *format_buttons)

                    row_index += 1

    return kb_obj.as_markup()
