import asyncio
from .base import database
from .user import Users as UserTable
from .fingerprint import Fingerprints as FingerprintTable
from .metadata import Metadata as MetadataTable
from .channels import Channels as ChannelTable


async def init():
    await database.create_tables(UserTable, FingerprintTable, MetadataTable, ChannelTable)


asyncio.run(init())

__all__ = (
    "UserTable",
    "FingerprintTable",
    "MetadataTable",
    "ChannelTable"
)
