from vkbottle import GroupEventType
from vkbottle.bot import Blueprint, Message, MessageEvent
from misc.handler_utils import commands_to_regex
from misc.models import Server
from misc.custom_rules import PayloadRule

bp = Blueprint('common commands available anywhere')
bp.labeler.vbml_ignore_case = True


@bp.on.private_message(text=('профиль', 'profile'))
@bp.on.message(regexp=commands_to_regex('profile', 'профиль'))
async def profile_handler(message: Message, server: Server, userdata, localization):
    user = (await bp.api.users.get(user_ids=message.from_id))[0]
    nickname = userdata.nickname or f'{user.first_name} {user.last_name}'

    await message.reply(localization.TID_PROFILE_TEXT.format(**{
        'name': f'[id{user.id}|{user.first_name}]',
        'nickname': f'[id{user.id}|{nickname}]',
        'bot_id': userdata.id,
        'platform': server.messenger,
        'platform_id': message.from_id,
        'rank': userdata.rank,
        'warnings': userdata.warns,
        'bind': userdata.tg_id or localization.HAVE_NOT_BINDING
        }))

@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'type': 'show_snackbar'}))
async def show_snackbar_handler(event: MessageEvent, localization):
    await event.show_snackbar(localization[event.payload['TID']])
