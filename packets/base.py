from box import Box
from bson import json_util


class Packet:
    def __init__(self, packet_id, *args, **kwargs):
        self.buffer = Box()
        self.pid = packet_id
        self.payload = args or kwargs or {}

    @property
    def pid(self):
        return self.buffer.packet_id

    @pid.setter
    def pid(self, value):
        self.buffer.packet_id = int(value)

    @property
    def payload(self):
        return self.buffer.payload

    @payload.setter
    def payload(self, value):
        if isinstance(value, tuple):
            value = value[0]
        if isinstance(value, str):
            value = json_util.loads(value)
        self.buffer.payload = value

    @property
    def str_payload(self):
        return json_util.dumps(self.buffer.payload)

    def encode(self):
        return f"{self.pid}::{self.str_payload}#".encode()

    @classmethod
    def decode(cls, data: str):
        data = data.split("::")
        return Packet(data[0], data[1])
