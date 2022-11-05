from pydantic import BaseModel
from typing import Any


class UserObject(BaseModel):
    vk_id: int = None
    tg_id: int = None
    set_key: str = None
    set_value: Any = None


class FingerprintObject(BaseModel):
    version: str = None
    major_v: int = None
    build_v: int = None
    revision_v: int = None
    sha: str = None
