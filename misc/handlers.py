from database import FingerprintTable
from managers import game, connections


class Handlers:
    def __init__(self, game_manager: game.GameManager, connections_manager: connections.ConnectionsManager):
        self.gm = game_manager
        self.cm = connections_manager
        self.handlers = set()

    def init_handlers(self):
        self.handlers.add(self.prod_handler())

    async def prod_handler(self):
        version = await FingerprintTable.get_or_none(is_actual=True)
        if version:
            version = f"{version.major_v}.{version.build_v}.{version.revision_v}"
        else:
            version = (await self.gm.get_market_data(1)).version

        async for game_data in self.gm.handle_server_update(version):
            game_data.blog_links = await self.gm.get_release_notes()
            if game_data.server_code == 7:
                raw_version = game_data.fingerprint.version.split('.')
                if actual_sha := await FingerprintTable.get_or_none(is_actual=True):
                    actual_sha = actual_sha.sha

                if actual_sha != game_data.fingerprint.sha:
                    await FingerprintTable.get_and_update(FingerprintTable.is_actual == True, is_actual=False)
                    await FingerprintTable.get_or_create(sha=game_data.fingerprint.sha, major_v=raw_version[0],
                                                         build_v=raw_version[1], revision_v=raw_version[2])
            elif game_data.server_code == 8:
                # Здесь будет рассылка пакетов ботам
                pass

            elif game_data.server_code == 10:
                # Здесь будет рассылка пакетов ботам
                if game_data.maintenance_is_end:
                    pass
                else:
                    pass
