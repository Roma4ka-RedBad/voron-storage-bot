from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DownloadCallback(CallbackData, prefix="download"):
    action: str
    file_id: int


def download_kb(localization, file_id: int):
    kb_obj = InlineKeyboardBuilder()
    kb_obj.row(InlineKeyboardButton(text=localization.TID_DOWNLOADFILES_BUTTON,
                                    callback_data=DownloadCallback(action="archive", file_id=file_id).pack()))

    return kb_obj.as_markup()
