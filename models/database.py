from pydantic import BaseModel
from typing import Any


class UserModel(BaseModel):
    vk_id: int = 0
    tg_id: int = 0
    set_key: str = None
    set_value: Any = None
