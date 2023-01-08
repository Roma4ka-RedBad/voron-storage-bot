from aiogram import Bot


async def delete_message(instance, packet):
    if packet.payload.platform_name == "TG":
        bot = Bot(token=await instance.server_instance.get_bot_token(), parse_mode='HTML')
        try:
            for message_id in packet.payload.message_ids:
                await bot.delete_message(chat_id=packet.payload.chat_id, message_id=message_id)
        except:
            pass
        await bot.session.close()
