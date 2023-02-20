from bot_config import Config


async def send_message(instance, packet):
    if packet.payload.platform_name == "VK":
        if isinstance(packet.payload.chat_ids, int):
            packet.payload.chat_ids = [packet.payload.chat_ids]

        for chat_id in packet.payload.chat_ids:
            await Config.bot_api.messages.send(peer_id=chat_id,
                                               message=packet.payload.text,
                                               random_id=0)
