from database import FingerprintTable
from managers.messengers import MessengersManager
from managers.game import GameManager


class Handlers:
    def __init__(self, game_manager: GameManager, messengers_manager: MessengersManager):
        self.gm = game_manager
        self.mm = messengers_manager
        self.handlers = set()

    def init_handlers(self):
        self.handlers.add(self.prod_handler())

    async def prod_handler(self):
        version = FingerprintTable.get_or_none(is_actual=True)
        if version:
            version = f"{version.major_v}.{version.build_v}.{version.revision_v}"
        else:
            version = (await self.gm.get_market_data(1)).version

        async for game_data in self.gm.handle_server_update(version):
            if game_data.server_code == 7:
                raw_version = game_data.fingerprint.version.split('.')
                if actual_sha := FingerprintTable.get_or_none(is_actual=True):
                    actual_sha = actual_sha.sha

                if actual_sha != game_data.fingerprint.sha:
                    FingerprintTable.update(is_actual=False).where(FingerprintTable.is_actual).execute()
                    FingerprintTable.get_or_create(sha=game_data.fingerprint.sha, major_v=raw_version[0],
                                                   build_v=raw_version[1], revision_v=raw_version[2])

            elif game_data.server_code == 10:
                print(f'Start maintenance! Time: {game_data.maintenance_end_time}')