from pydantic import BaseModel


class ClientObject(BaseModel):
    messenger: str