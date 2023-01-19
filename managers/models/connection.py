import asyncio
import random


class Connection:
    def __init__(self, transport: asyncio.Transport):
        self.transport = transport
        self.is_handler = False
        self.transport_id = random.randint(0, 10000000)

    async def send(self, packet):
        self.transport.write(packet.encode())

    async def close(self):
        self.transport.close()

    def __repr__(self):
        return f"<Connection id={self.transport_id} handler={self.is_handler}>"
