from aiogram import Bot


async def edit_message(instance, packet):
    bot = Bot(token=await instance.server_instance.get_bot_token(), parse_mode='HTML')
    await bot.edit_message_text(message_id=packet.payload.message_id, text=packet.payload.text, chat_id=packet.payload.chat_id)
    await bot.session.close()
