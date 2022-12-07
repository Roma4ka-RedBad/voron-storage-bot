import toml
from box import Box


class Config(Box):
    IMAGES = ['ktx', 'pvr', 'png', 'jpg']
    AUDIO = ['mp3', 'ogg', 'wav', 'flac', 'ape', 'aiff', 'swa', 'psf', 'aac', 'alac', 'dsd']
    MODELS = ['scw', 'glb', 'dae', 'obj', 'fbx']
    CSV = ['decompress', 'compress']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_converts(cls):
        converts = Box()

        cls._add_list_converts(converts, cls.AUDIO)
        cls._add_list_converts(converts, cls.IMAGES)
        cls._add_list_converts(converts, cls.MODELS)

        converts.csv = cls.CSV
        converts.sc = ['png']
        converts.png.append('sc')
        converts.scw.append('update')

        return converts

    @staticmethod
    def _add_list_converts(main_obj, obj: list):
        for arg in obj:
            copy_obj = obj.copy()
            copy_obj.remove(arg)
            main_obj[arg] = copy_obj


Config = Config(toml.load('config.toml'))
