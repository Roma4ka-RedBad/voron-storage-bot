from vkbottle.bot import Blueprint, Message
from misc.handler_utils import commands_to_regex, get_nickname
from misc.models import Server
from misc.custom_rules import StartFromRule


bp = Blueprint('profile commands')
bp.labeler.vbml_ignore_case = True


@bp.on.private_message(text=('профиль', 'profile'))
@bp.on.message(regexp=commands_to_regex('profile', 'профиль'))
async def profile_handler(message: Message, server: Server, userdata, localization):
    user = await message.get_user()
    nickname = userdata.nickname or user.first_name

    await message.reply(localization.TID_PROFILE_TEXT.format(**{
        'name': f'[id{user.id}|{user.first_name}]',
        'nickname': await get_nickname(userdata, bp.api),
        'bot_id': userdata.id,
        'platform': server.messenger,
        'platform_id': message.from_id,
        'rank': userdata.rank,
        'warnings': userdata.warns,
        'bind': userdata.tg_id or localization.TID_FAIL
        }))


@bp.on.message(StartFromRule(regex_pattern=commands_to_regex('Изменить ник', 'Change nick', 'ник', 'nick')))
@bp.on.private_message(StartFromRule('Изменить ник', 'Change nick', 'ник', 'nick', args_must_be=False))
async def change_nickname_handler(message: Message, localization, server, userdata):
    if len(message.text) == 0:
        await message.reply(localization.TID_CHANGE_NICK_WITHOUT_ARGS.format(
            name=await get_nickname(userdata, bp.api)))
        return

    user = await server.send_message('user/set',
                                     vk_id=userdata.vk_id,
                                     tg_id=userdata.tg_id,
                                     set_key='nickname',
                                     set_value=message.text)
    await message.reply(localization.TID_SETNAME_DONE.format(name=user.content.nickname))


@bp.on.private_message(text=('Привязать к TG', 'Bind to TG'))
@bp.on.message(regexp=commands_to_regex('Изменить ник', 'Bind to TG'))
async def binding_without_arguments_handler(message: Message, localization):
    await message.reply(localization.TID_COMMAND_IN_DEVELOPMENT)
