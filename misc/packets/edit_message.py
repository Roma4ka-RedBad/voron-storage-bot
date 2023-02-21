from bot_config import Config


async def edit_message(instance, packet):

    if packet.payload.platform_name == 'VK':
        if packet.payload.form_args.total_files_count % 10 == 0:
            await Config.bot_api.messages.edit(
                    conversation_message_id=packet.payload.message_id,
                    peer_id=packet.payload.chat_id,
                    message=Config.localizations[packet.payload.language_code][packet.payload.tid].format(
                        **packet.payload.form_args)
            )
