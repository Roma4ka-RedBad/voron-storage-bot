from database import ChannelTable
from database import FingerprintTable
from managers import connections
from packets.base import Packet


class Handlers:
    def __init__(self, game_manager, connections_manager: connections.ConnectionsManager):
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
                channels = await ChannelTable.get_list(ChannelTable.prod_update_mailing == True)
                for channel in channels:
                    await self.cm.send_by_handlers(Packet(20100, platform_name=channel.platform_name,
                                                          chat_id=channel.channel_id,
                                                          text=channel.mailing_data.prod_update.text,
                                                          form_args=game_data))

            elif game_data.server_code == 10:
                channels = await ChannelTable.get_list(ChannelTable.prod_maintenance_mailing == True)
                for channel in channels:
                    if game_data.maintenance_is_end:
                        await self.cm.send_by_handlers(Packet(20100, platform_name=channel.platform_name,
                                                              chat_id=channel.channel_id,
                                                              text=channel.mailing_data.prod_maintenance_end.text,
                                                              form_args=game_data))
                    else:
                        await self.cm.send_by_handlers(Packet(20100, platform_name=channel.platform_name,
                                                              chat_id=channel.channel_id,
                                                              text=channel.mailing_data.prod_maintenance_start.text,
                                                              form_args=game_data))
