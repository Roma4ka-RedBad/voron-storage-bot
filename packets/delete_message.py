from bot_config import Config


async def delete_message(instance, packet):
    if packet.payload.platform_name == "VK":
        await Config.bot_api.messages.delete(peer_id=packet.payload.chat_id,
                                             cmids=packet.payload.message_ids,
                                             delete_for_all=True)
