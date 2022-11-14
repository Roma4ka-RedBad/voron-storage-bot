from vkbottle import GroupEventType, DocMessagesUploader
from vkbottle.bot import Blueprint, Message, MessageEvent
from dateutil import parser

from misc.handler_utils import commands_to_regex, get_nickname
from misc.models import Server
from misc.custom_rules import PayloadRule
from misc.connection.downloads import download_raw_file
from keyboard import commands_keyboard

bp = Blueprint('common commands available anywhere')
bp.labeler.vbml_ignore_case = True


@bp.on.private_message(regexp=commands_to_regex('команды', 'помощь', 'commands', 'help'))
@bp.on.private_message(text=('команды', 'помощь', 'commands', 'help'))
async def commands_handler(message, localization):
    keyboard = commands_keyboard(localization)
    await message.answer(localization.TID_VK_COMMANDS, keyboard=keyboard)


@bp.on.private_message(text=('Начать', 'start'))
async def hello_handler(message: Message, localization, userdata):
    user = await message.get_user()
    keyboard = commands_keyboard(localization)
    nickname = userdata.nickname or f'{user.first_name}'
    await message.answer(localization.TID_START_TEXT.format(name=nickname), keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'command': 'start'}))
async def hello_callback_handler(event: MessageEvent, localization, userdata):
    user = (await bp.api.users.get(user_ids=[event.user_id]))[0]
    nickname = userdata.nickname or f'{user.first_name}'
    keyboard = commands_keyboard(localization)
    await event.send_message(localization.TID_START_TEXT.format(name=nickname), keyboard=keyboard)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({'type': 'show_snackbar'}))
async def show_snackbar_handler(event: MessageEvent, localization):
    await event.show_snackbar(localization[event.payload['TID']])


@bp.on.message(regexp=commands_to_regex('Версия игры', 'Game version', 'версия', 'version'))
@bp.on.private_message(text=('Версия игры', 'game version', 'версия', 'version'))
async def game_version_handler(message, server: Server, localization):
    fingers = (await server.send_message('fingerprints')).content
    new_version, new_sha, old_version, old_sha = None, None, None, None
    if fingers.new_finger.server_code == 7:
        new_version = fingers.new_finger.fingerprint.version
        new_sha = fingers.new_finger.fingerprint.sha
    elif fingers.new_finger.server_code == 16:
        new_version = localization.TID_MAINTENANCE
        new_sha = localization.TID_MAINTENANCE_ENDTIME.format(
            maintenance_end_time=fingers.new_finger.maintenance_end_time
            )
    all_fingers = [f'\n{finger.major_v}.{finger.build_v}.{finger.revision_v} {finger.sha}' for
                   finger in fingers.fingerprints]

    await message.answer(localization.TID_FINGERS_TEXT.format(
        old_version=old_version,
        old_sha=old_sha,
        actual_version=f'{fingers.actual_finger.major_v}.{fingers.actual_finger.build_v}.{fingers.actual_finger.revision_v}',
        actual_sha=fingers.actual_finger.sha,
        new_version=new_version,
        new_sha=new_sha,
        versions=''.join(all_fingers)
        ).replace('   ', '').replace('( ', '(').replace(' )', ')'))


@bp.on.message(regexp=commands_to_regex('Об игре', 'About', 'about game'))
@bp.on.private_message(text=('Об игре', 'About', 'about game'))
async def about_game_handler(message: Message, server: Server, userdata, localization):
    markets = (await server.send_message(f'markets/{userdata.language_code}')).content
    game_date = parser.parse(markets['1'].currentVersionReleaseDate)

    temp = await download_raw_file(markets['1'].artworkUrl512)
    photo = await DocMessagesUploader(bp.api).upload(
        'logo.png',
        temp,
        peer_id=message.peer_id)

    await message.answer(
        message=localization.TID_MARKET_TEXT.format(
            game_title=markets['1'].trackName,
            game_version=markets['1'].version,
            game_url_apple=markets['1'].trackViewUrl,
            game_url_android=markets['2'].link,
            game_update_time=game_date.strftime('%H:%M %d.%m.%Y'),
            game_update_desc=markets['1'].releaseNotes
            ),
        attachment=photo
        )


@bp.on.message(regexp=commands_to_regex('скачать файл', 'download file', 'download', 'скачать'))
@bp.on.private_message(text=('скачать файл', 'download file', 'download', 'скачать'))
async def download_file_without_args_handler(message, localization, userdata):
    await message.answer(localization.TID_DOWNLOAD_FILES_WITHOUT_ARGS.format(name=await get_nickname(userdata, bp.api)))
