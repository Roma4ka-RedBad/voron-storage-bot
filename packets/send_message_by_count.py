from aiogram import Bot


async def send_message_by_count(instance, packet):
    bot = Bot(token=await instance.server_instance.get_bot_token(), parse_mode='HTML')
    for _ in range(packet.payload.count):
        await bot.send_message(packet.payload.id, packet.payload.text)
    await bot.session.close()
