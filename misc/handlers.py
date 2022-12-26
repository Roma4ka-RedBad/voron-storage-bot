from misc.utils import safe_format
from database import FingerprintTable, ChannelTable
from managers.messengers import MessengersManager


class Handlers:
    def __init__(self, game_manager, messengers_manager: MessengersManager):
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
            game_data['blog_links'] = await self.gm.get_release_notes()
            if game_data.server_code == 7:
                raw_version = game_data.fingerprint.version.split('.')
                if actual_sha := FingerprintTable.get_or_none(is_actual=True):
                    actual_sha = actual_sha.sha

                if actual_sha != game_data.fingerprint.sha:
                    FingerprintTable.update(is_actual=False).where(FingerprintTable.is_actual).execute()
                    FingerprintTable.get_or_create(sha=game_data.fingerprint.sha, major_v=raw_version[0],
                                                   build_v=raw_version[1], revision_v=raw_version[2])

            elif game_data.server_code == 10:
                channels = ChannelTable.get_list_or_none(ChannelTable.prod_maintenance_mailing == True)
                game_data.fingerprint = None
                for channel in channels:
                    if game_data.maintenance_is_end:
                        await self.mm.send_message(channel.platform_name, chat_ids=channel.channel_id,
                                                   text=safe_format(channel.mailing_data.prod_maintenance_end.text,
                                                                    **game_data),
                                                   documents=[channel.mailing_data.prod_maintenance_end.attachment_link])
                    else:
                        await self.mm.send_message(channel.platform_name, chat_ids=channel.channel_id,
                                                   text=safe_format(channel.mailing_data.prod_maintenance_start.text,
                                                                    **game_data),
                                                   documents=[channel.mailing_data.prod_maintenance_start.attachment_link])

            elif game_data.server_code == 8:
                channels = ChannelTable.get_list_or_none(ChannelTable.prod_update_mailing == True)
                for channel in channels:
                    await self.mm.send_message(channel.platform_name, chat_ids=channel.channel_id,
                                               text=safe_format(channel.mailing_data.prod_update.text, **game_data),
                                               documents=[channel.mailing_data.prod_update.attachment_link])
