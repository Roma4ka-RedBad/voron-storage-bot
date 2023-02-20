from vkbottle.bot import Message

from bot_config import Config
from misc.connections import ServerConnection
from misc.handler_utils import commands_to_regex
from misc.packets import Packet

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.message(regexp=commands_to_regex('Версия игры', 'Game version', 'версия', 'version'))
@labeler.private_message(text=('Версия игры', 'game version', 'версия', 'version'))
async def game_version_handler(message: Message, server: ServerConnection, localization):
    fingers = await server.send(Packet(13100))
    if fingers:
        fingers = fingers.payload
    new_version, new_sha, old_version, old_sha = None, None, None, None

    if fingers.new_finger.server_code == 7:
        new_version = fingers.new_finger.fingerprint.version
        new_sha = fingers.new_finger.fingerprint.sha
    elif fingers.new_finger.server_code == 16:
        new_version = localization.FINGERS_MAINTENANCE_ACTIVE
        new_sha = localization.FINGERS_MAINTENANCE_ENDTIME.format(
                maintenance_end_time=fingers.new_finger.maintenance_end_time)

    all_fingers = [f'\n{finger.major_v}.{finger.build_v}.{finger.revision_v} {finger.sha}' for
                   finger in fingers.fingerprints]

    await message.answer(localization.FINGERS_BODY.format(
            old_version=old_version,
            old_sha=old_sha,
            actual_version=f'{fingers.actual_finger.major_v}.{fingers.actual_finger.build_v}.'
                           f'{fingers.actual_finger.revision_v}',
            actual_sha=fingers.actual_finger.sha,
            new_version=new_version,
            new_sha=new_sha,
            versions=''.join(all_fingers)
    ).replace('   ', '').replace('( ', '(').replace(' )', ')'))
