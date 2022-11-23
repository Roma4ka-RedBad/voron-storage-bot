import toml
from box import Box

Config = Box(toml.load('config.toml'))
