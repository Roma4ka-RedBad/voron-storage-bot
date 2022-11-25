from pydantic import BaseModel


class Metadata(BaseModel):
    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __getattr__(self, item):
        self.__dict__[item] = None
        return None
