from .base import database
from .user import Users as UserTable
from .fingerprint import Fingerprints as FingerprintTable
from .metadata import Metadata as MetadataTable

database.create_tables([UserTable, FingerprintTable, MetadataTable], safe=True)

__all__ = (
    "UserTable",
    "FingerprintTable",
    "MetadataTable"
)
