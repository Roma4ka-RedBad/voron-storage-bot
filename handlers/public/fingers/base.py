from aiogram.types import Message
from aiogram.utils.markdown import hcode, hbold

from misc.models import Server


async def command_fingers(message: Message, server: Server, user_localization):
    if not user_localization:
        return await message.answer(text='Подключение к серверу отсутствует!')

    fingers = (await server.send_msg('fingerprints')).content
    new_version, new_sha = None, None
    if fingers.new_finger.server_code == 7:
        new_version = fingers.new_finger.fingerprint.version
        new_sha = fingers.new_finger.fingerprint.sha
    elif fingers.new_finger.server_code == 16:
        new_version = user_localization.TID_MAINTENANCE
        new_sha = user_localization.TID_MAINTENANCE_ENDTIME.format(
            maintenance_end_time=fingers.new_finger.maintenance_end_time
        )
    all_fingers = [hcode(f"\n{finger.major_v}.{finger.build_v}.{finger.revision_v}") + f" {hcode(finger.sha)}" for
                   finger in fingers.fingerprints]

    await message.answer(text=hbold(user_localization.TID_FINGERS_TEXT).format(
        old_version=hcode(f"{fingers.old_finger.major_v}.{fingers.old_finger.build_v}.{fingers.old_finger.revision_v}"),
        old_sha=hcode(fingers.old_finger.sha),
        actual_version=hcode(
            f"{fingers.actual_finger.major_v}.{fingers.actual_finger.build_v}.{fingers.actual_finger.revision_v}"),
        actual_sha=hcode(fingers.actual_finger.sha),
        new_version=hcode(new_version),
        new_sha=hcode(new_sha),
        versions=''.join(all_fingers)
    ))
