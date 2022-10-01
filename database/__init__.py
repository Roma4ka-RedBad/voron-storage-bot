from .base import database
from .user import User

database.create_tables([User], safe=True)

__all__ = (
    "User"
)
