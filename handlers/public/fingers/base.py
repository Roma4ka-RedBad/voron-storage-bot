from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server
from misc.utils import safe_split_text


async def command_fingers(message: Message, server: Server, user_localization):
    if not user_localization:
        return await message.answer(text='Подключение к серверу отсутствует!')

    fingers = (await server.send_msg('fingerprints')).content
    new_version, new_sha, old_version, old_sha = None, None, None, None
    if fingers.new_finger.server_code == 7:
        new_version = fingers.new_finger.fingerprint.version
        new_sha = fingers.new_finger.fingerprint.sha
    elif fingers.new_finger.server_code == 10:
        new_version = user_localization.TID_MAINTENANCE
        new_sha = user_localization.TID_MAINTENANCE_ENDTIME.format(
            maintenance_end_time=fingers.new_finger.maintenance_end_time
        )
    if fingers.old_finger:
        old_version = f"{fingers.old_finger.major_v}.{fingers.old_finger.build_v}.{fingers.old_finger.revision_v}"
        old_sha = fingers.old_finger.sha
    all_fingers = ["\n" + hcode(f"{finger.major_v}.{finger.build_v}.{finger.revision_v}") + f" {hcode(finger.sha)}" for
                   finger in fingers.fingerprints]

    parts = await safe_split_text(user_localization.TID_FINGERS_TEXT.format(
        old_version=hcode(old_version),
        old_sha=hcode(old_sha),
        actual_version=hcode(
            f"{fingers.actual_finger.major_v}.{fingers.actual_finger.build_v}.{fingers.actual_finger.revision_v}"),
        actual_sha=hcode(fingers.actual_finger.sha),
        new_version=hcode(new_version),
        new_sha=hcode(new_sha),
        versions=''.join(all_fingers)
    ), split_separator='\n', length=3900)

    for part in parts:
        await message.answer(hbold(part).replace('&lt;', '<').replace('&gt;', '>'))
