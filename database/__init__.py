from .base import database
from .user import Users as UserTable

database.create_tables([UserTable], safe=True)

__all__ = (
    "UserTable"
)
