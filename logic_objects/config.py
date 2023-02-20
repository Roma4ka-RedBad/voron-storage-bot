import toml
from box import Box


class Config(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


Config = Config(toml.load('config.toml'))
