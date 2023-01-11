from aiogram import Bot
from misc.utils import FormString


async def send_message(instance, packet):
    if packet.payload.platform_name == "TG":
        bot = Bot(token=await instance.server_instance.get_bot_token(), parse_mode='HTML')

        if isinstance(packet.payload.chat_ids, int):
            packet.payload.chat_ids = [packet.payload.chat_ids]
        if not packet.payload.get("form_args", None):
            packet.payload.form_args = {}

        for chat_id in packet.payload.chat_ids:
            try:
                await bot.send_message(chat_id=chat_id,
                                       text=FormString.paste_args(packet.payload.text, **packet.payload.form_args))
            except:
                pass
        await bot.session.close()
