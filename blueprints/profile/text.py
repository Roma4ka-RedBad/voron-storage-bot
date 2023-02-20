from vkbottle.bot import Message

from bot_config import Config
from keyboards import change_language_keyboard
from misc.connections import ServerConnection
from misc.custom_rules import StartFromRule
from misc.handler_utils import commands_to_regex, get_nickname
from misc.models import UserModel
from misc.packets import Packet

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.private_message(text=('профиль', 'profile'))
@labeler.message(regexp=commands_to_regex('profile', 'профиль'))
async def profile_handler(message: Message, userdata: UserModel, localization):
    user = await message.get_user()

    await message.reply(
            message=localization.PROFILE_BODY.format(
                    name=f'[id{user.id}|{user.first_name}]',
                    nickname=await get_nickname(userdata),
                    bot_id=userdata.id,
                    platform='VK',
                    platform_id=message.from_id,
                    rank=userdata.rank,
                    warnings=userdata.warns,
                    bind=userdata.tg_id or localization.MISSING_ERROR
            ),
            keyboard=change_language_keyboard(localization))


@labeler.message(StartFromRule(regex_pattern=commands_to_regex('Изменить ник', 'Change nick', 'ник', 'nick')))
@labeler.private_message(StartFromRule('Изменить ник', 'Change nick', 'ник', 'nick', args_must_be=False))
async def change_nickname_handler(message: Message, userdata: UserModel, server: ServerConnection, localization):
    if len(message.text) == 0:
        await message.reply(localization.SETNAME_WITHOUT_ARGS.format(name=await get_nickname(userdata)))
        return

    user = await server.send(Packet(11101, vk_id=userdata.vk_id, set_key='nickname', set_value=message.text))
    await message.reply(localization.SETNAME_DONE.format(name=user.payload.nickname))


@labeler.private_message(text=('Привязать к TG', 'Bind to TG'))
@labeler.message(regexp=commands_to_regex('Изменить ник', 'Bind to TG'))
async def binding_without_arguments_handler(message: Message, localization):
    await message.reply(localization.COMMAND_IN_DEVELOPMENT_ERROR)
