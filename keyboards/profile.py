from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ProfileCallback(CallbackData, prefix="start"):
    action: str
    language_code: str = None


def profile_kb(language: str, localization):
    kb_obj = InlineKeyboardBuilder()
    kb_obj.row(InlineKeyboardButton(text=localization.TID_SET_LANGUAGE,
                                    callback_data=ProfileCallback(action="set_language", language_code=language).pack()))

    return kb_obj.as_markup()
