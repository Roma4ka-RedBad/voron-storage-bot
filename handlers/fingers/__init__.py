from aiogram.types import Message
from aiogram.utils.markdown import hcode

from misc.utils import FormString
from packets.base import Packet


async def command_fingers(message: Message, localization, server):
    packet = await server.send(Packet(13100))
    if packet:
        new_version, new_sha, old_version, old_sha = None, None, None, None
        if packet.payload.new_finger.server_code == 7:
            new_version = packet.payload.new_finger.fingerprint.version
            new_sha = packet.payload.new_finger.fingerprint.sha
        elif packet.payload.new_finger.server_code == 10:
            new_version = localization.FINGERS_MAINTENANCE_ACTIVE
            new_sha = FormString.paste_args(localization.FINGERS_MAINTENANCE_ENDTIME,
                                            maintenance_end_time=packet.payload.new_finger.maintenance_end_time
                                            )

        if packet.payload.old_finger:
            old_version = f"{packet.payload.old_finger.major_v}.{packet.payload.old_finger.build_v}.{packet.payload.old_finger.revision_v}"
            old_sha = packet.payload.old_finger.sha

        all_fingers = ["\n" + hcode(f"{finger.major_v}.{finger.build_v}.{finger.revision_v}") + f" {hcode(finger.sha)}"
                       for finger in packet.payload.fingerprints]

        parts = FormString(localization.FINGERS_BODY, split_length=3900, split_separator="\n")
        parts = parts.get_form_string(
            set_style="bold",
            with_parts=True,
            old_version=hcode(old_version),
            old_sha=hcode(old_sha),
            actual_version=hcode(
                f"{packet.payload.actual_finger.major_v}.{packet.payload.actual_finger.build_v}.{packet.payload.actual_finger.revision_v}"),
            actual_sha=hcode(packet.payload.actual_finger.sha),
            new_version=hcode(new_version),
            new_sha=hcode(new_sha),
            versions=''.join(all_fingers)
        )

        [await message.answer(part) for part in parts]
