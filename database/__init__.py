from .base import database
from .user import Users as UserTable
from .fingerprint import Fingerprints as FingerprintTable
from .metadata import Metadata as MetadataTable
from .channels import Channels as ChannelTable

database.create_tables([UserTable, FingerprintTable, MetadataTable, ChannelTable], safe=True)

__all__ = (
    "UserTable",
    "FingerprintTable",
    "MetadataTable",
    "ChannelTable"
)
