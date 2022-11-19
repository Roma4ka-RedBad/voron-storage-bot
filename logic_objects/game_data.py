from pydantic import BaseModel
from pathlib import Path


class GameData(BaseModel):
    major_v: int = None
    build_v: int = None
    revision_v: int = 1
    search_query: str = ''
    path: Path = None
