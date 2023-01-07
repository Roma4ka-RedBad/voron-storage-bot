from aiogram import Bot
from misc.utils import FormString


async def edit_message(instance, packet):
    if packet.payload.platform_name == "TG":
        bot = Bot(token=await instance.server_instance.get_bot_token(), parse_mode='HTML')
        localization = instance.config_data.localization
        try:
            await bot.edit_message_text(message_id=packet.payload.message_id,
                                        text=FormString.paste_args(
                                            localization[packet.payload.language_code][packet.payload.tid],
                                            **packet.payload.form_args),
                                        chat_id=packet.payload.chat_id)
        except:
            pass
        await bot.session.close()
