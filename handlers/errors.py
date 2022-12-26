from aiogram import Bot
from aiogram.types import Update
from aiograph import Telegraph
from datetime import datetime
import traceback


async def error_handler(update: Update, bot: Bot, server_config):
    telegraph = Telegraph(server_config.TG.telegraph_token)
    use_class, message_id, chat_id = None, None, None
    if update.message:
        use_class = update.message
        chat_id = use_class.chat.id
        message_id = use_class.message_id
    elif update.callback_query:
        use_class = update.callback_query
        chat_id = use_class.message.chat.id
        message_id = use_class.message.message_id

    content = f"Дата: {datetime.now()}\n" \
              f"Пользователь: {use_class.from_user.full_name}\n" \
              f"Чат: {chat_id} (сообщение: {message_id})\n" \
              f"Traceback:\n{traceback.format_exc()}"
    page = await telegraph.create_page('Traceback Error', content=content)
    await telegraph.close()

    await use_class.answer("Произошла ошибка! Попробуйте позже...")
    if server_config:
        for admin in server_config.TG.admins_ids:
            try:
                await bot.send_message(chat_id=admin, text=f"Произошла ошибка!\n{page.url}")
            except:
                pass
