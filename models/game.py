from pydantic import BaseModel


class GameObject(BaseModel):
    major: int
    minor: int
    revision: int
    host: str
    port: int = 9339
