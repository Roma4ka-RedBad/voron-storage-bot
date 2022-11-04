from pydantic import BaseModel
from typing import Any


class UserObject(BaseModel):
    vk_id: int = None
    tg_id: int = None
    set_key: str = None
    set_value: Any = None