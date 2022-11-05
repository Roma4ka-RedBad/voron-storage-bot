from .base import database
from .user import Users as UserTable
from .fingerprint import Fingerprints as FingerprintTable

database.create_tables([UserTable, FingerprintTable], safe=True)

__all__ = (
    "UserTable",
    "FingerprintTable"
)
