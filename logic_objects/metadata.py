class Metadata:
    def __init__(self, data: dict):
        for k, v in data.items():
            self.__dict__[k] = v

    def __getattr__(self, item):
        self.__dict__[item] = None
        return None
