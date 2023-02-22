from ..base import Packet
from database import FingerprintTable


# 13100
async def brawlstars_get_fingers(instance, packet: Packet, game_manager):
    actual_finger = await FingerprintTable.get(is_actual=True)
    new_finger = await game_manager.server_data(actual_finger.major_v, actual_finger.build_v, actual_finger.revision_v, use_sync=True)
    old_finger = await FingerprintTable.get_or_none(FingerprintTable.id == (actual_finger.id - 1))
    new_finger.fingerprint = {"version": new_finger.fingerprint.version,
                              "sha": new_finger.fingerprint.sha} if getattr(new_finger, 'fingerprint', None) else None
    await instance.client_connection.send(
        Packet(packet.pid,
               actual_finger=actual_finger.__data__,
               new_finger=new_finger,
               old_finger=old_finger.__data__ if old_finger else None,
               fingerprints=[finger.__data__ for finger in
                             await FingerprintTable.select().order_by(-FingerprintTable.major_v,
                                                                      -FingerprintTable.build_v)]
    ))
