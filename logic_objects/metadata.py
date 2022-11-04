from pydantic import BaseModel


class Metadata(BaseModel):
    def __init__(self, data: dict):
        super().__init__()
        for k, v in data.items():
            self.__dict__[k] = v

    def __getattr__(self, item):
        self.__dict__[item] = None
        return None
