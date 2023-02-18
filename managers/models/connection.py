import asyncio


class Connection:
    unique_id = 0

    def __init__(self, transport: asyncio.Transport):
        self.transport = transport
        self.is_handler = False
        self.transport_id = self._get_unique_id()

    async def send(self, packet):
        self.transport.write(packet.encode())

    async def close(self):
        self.transport.close()

    def _get_unique_id(self) -> int:
        self.__class__.unique_id += 1

        if self.__class__.unique_id > 1_000_000:
            self.__class__.unique_id = 0

        return self.__class__.unique_id

    def __repr__(self):
        return f"<Connection id={self.transport_id} handler={self.is_handler}>"
