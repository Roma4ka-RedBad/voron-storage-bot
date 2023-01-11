from aiogram import Bot
from misc.utils import FormString


async def send_message(instance, packet):
    if packet.payload.platform_name == "TG":
        bot = Bot(token=await instance.server_instance.get_bot_token(), parse_mode='HTML')
        try:
            await bot.send_message(chat_id=packet.payload.chat_id,
                                   text=FormString.paste_args(packet.payload.text, **packet.payload.form_args))
        except:
            pass
        await bot.session.close()
