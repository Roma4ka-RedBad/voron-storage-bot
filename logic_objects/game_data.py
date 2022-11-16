from pydantic import BaseModel


class GameData(BaseModel):
    major_v: int = None
    build_v: int = None
    revision_v: int = 1
    search_query: str = ''
