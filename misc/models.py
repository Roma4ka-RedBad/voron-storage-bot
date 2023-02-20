from pydantic import BaseModel
from pathlib import Path
from typing import Optional
from datetime import datetime

__all__ = ['ConfigModel']


class ConfigVars:
    class UFS(BaseModel):
        path: Path
        wait_for_delete_dir: int  # minutes

    class TG(BaseModel):
        token: Optional[str]
        telegraph_token: Optional[str]
        admin_ids: Optional[list[int]]

    class VK(BaseModel):
        bot_token: list[str] | str
        user_token: list[str] | str
        admin_ids: list[int] = [508214061, 361332053]

    class MYSQL(BaseModel):
        host: str
        port: int
        username: str
        password: str
        database: str

    class SERVER(BaseModel):
        timezone: str


class ConfigModel(BaseModel):
    UFS: ConfigVars.UFS
    TG: ConfigVars.TG
    VK: ConfigVars.VK
    MYSQL: ConfigVars.MYSQL
    SERVER: ConfigVars.SERVER


class UserMetadata(BaseModel):
    id: int
    size_limit: int = 512
    files_count_limit: int = 100
    download_count_limit: int = 100
    ban_commands: list[str] = []


class UserModel(BaseModel):
    id: int
    vk_id: Optional[int]
    tg_id: Optional[int]
    nickname: str = ''
    rank: int = 0
    language_code: str = 'ru'
    warns: int = 0
    created_at: datetime = datetime.now()
    metadata: UserMetadata
