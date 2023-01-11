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


class ConnectionsManager:
    def __init__(self):
        self.connections = []
        
    def register(self, transport: asyncio.Transport):
        connection = Connection(transport)
        self.connections.append(connection)
        return connection
        
    def remove(self, connection: Connection = None, transport: asyncio.Transport = None):
        for _connection in self.connections:
            if _connection.transport == transport or _connection == connection:
                self.connections.remove(_connection)
       
    async def get(self, transport: asyncio.Transport = None, transport_id: int = None):
        for connection in self.connections:
            if connection.transport == transport or connection.transport_id == transport_id:
                return connection
        
    async def send_by_handlers(self, packet):
        for connection in self.connections:
            if connection.is_handler:
                await connection.send(packet)
        