from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

from config import bot_config
from keyboard import change_language_keyboard
from misc.custom_rules import StartFromRule, PayloadRule
from misc.handler_utils import commands_to_regex, get_nickname
from misc.models import Server

labeler = bot_config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.private_message(text=('профиль', 'profile'))
@labeler.message(regexp=commands_to_regex('profile', 'профиль'))
async def profile_handler(message: Message, server: Server, userdata, localization):
    user = await message.get_user()

    await message.reply(
        message=localization.TID_PROFILE_TEXT.format(**{
            'name': f'[id{user.id}|{user.first_name}]',
            'nickname': await get_nickname(userdata, bot_config.api),
            'bot_id': userdata.id,
            'platform': server.messenger,
            'platform_id': message.from_id,
            'rank': userdata.rank,
            'warnings': userdata.warns,
            'bind': userdata.tg_id or localization.TID_FAIL
        }),
        keyboard=change_language_keyboard(localization))


@labeler.message(StartFromRule(regex_pattern=commands_to_regex('Изменить ник', 'Change nick', 'ник', 'nick')))
@labeler.private_message(StartFromRule('Изменить ник', 'Change nick', 'ник', 'nick', args_must_be=False))
async def change_nickname_handler(message: Message, localization, server, userdata):
    if len(message.text) == 0:
        await message.reply(localization.TID_CHANGE_NICK_WITHOUT_ARGS.format(
            name=await get_nickname(userdata, bot_config.api)))
        return

    user = await server.send_message('user/set',
                                     vk_id=userdata.vk_id,
                                     tg_id=userdata.tg_id,
                                     set_key='nickname',
                                     set_value=message.text)
    await message.reply(localization.TID_SETNAME_DONE.format(name=user.content.nickname))


@labeler.private_message(text=('Привязать к TG', 'Bind to TG'))
@labeler.message(regexp=commands_to_regex('Изменить ник', 'Bind to TG'))
async def binding_without_arguments_handler(message: Message, localization):
    await message.reply(localization.TID_COMMAND_IN_DEVELOPMENT)


@labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'command': 'change_language'}))
async def hello_callback_handler(event: MessageEvent, userdata, server):
    user = (await bot_config.api.users.get(user_ids=[event.user_id]))[0]
    lg_code = {'ru': 'en', 'en': 'ru'}[userdata.language_code]
    userdata = (await server.send_message('user/set', vk_id=event.user_id, set_key='language_code',
                                          set_value=lg_code)).content
    localization = (await server.send_message(f'user/localization/{lg_code}')).content
    await event.edit_message(
        message=localization.TID_PROFILE_TEXT.format(**{
            'name': f'[id{user.id}|{user.first_name}]',
            'nickname': await get_nickname(userdata, bot_config.api),
            'bot_id': userdata.id,
            'platform': server.messenger,
            'platform_id': event.user_id,
            'rank': userdata.rank,
            'warnings': userdata.warns,
            'bind': userdata.tg_id or localization.TID_FAIL
        }),
        keyboard=change_language_keyboard(localization))
