from configparser import ConfigParser
from box import Box


class Config:
    def __init__(self, destination: str):
        self.config = ConfigParser()
        self.config.read(destination)
        self.get_box()

    def get(self, section: str, option: str):
        data = self.config.get(section, option)
        if data.isdigit():
            data = self.config.getint(section, option)
        elif data in ['true', 'false']:
            data = self.config.getboolean(section, option)

        return data

    def get_box(self):
        self.box = Box()
        for section in self.config.sections():
            if section not in self.box:
                self.box[section] = {}

            for option in self.config.options(section):
                self.box[section][option] = self.get(section, option)

        return self.box

    def get_size_by_format(self, file_format: str):
        if file_format in self.box.FILE_SIZE_LIMITS:
            return self.box.FILE_SIZE_LIMITS[file_format]
        else:
            return self.box.FILE_SIZE_LIMITS.default
