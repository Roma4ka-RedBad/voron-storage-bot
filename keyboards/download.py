from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DownloadCallback(CallbackData, prefix="download"):
    action: str
    object_id: int
    max_files_count: int


def download_kb(localization, object_id: int, max_files_count: int = 0):
    kb_obj = InlineKeyboardBuilder()
    kb_obj.row(InlineKeyboardButton(text=localization.DOWNLOADFILES_BUTTON,
                                    callback_data=DownloadCallback(action="archive", object_id=object_id,
                                                                   max_files_count=max_files_count).pack()))

    return kb_obj.as_markup()
