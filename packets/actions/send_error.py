from ..base import Packet
from logic_objects.config import Config
from managers.connections import ConnectionsManager


async def action_send_error(instance, packet: Packet, connections_manager: ConnectionsManager, traceback_text: str = None):
    if packet.payload.get("traceback_text", None):
        traceback_text = packet.payload.traceback_text

    if traceback_text:
        await connections_manager.send_by_handlers(
            Packet(20100, platform_name="TG", text=traceback_text, chat_ids=Config.TG.admin_ids))
        await connections_manager.send_by_handlers(
            Packet(20100, platform_name="VK", text=traceback_text, chat_ids=Config.VK.admin_ids))
