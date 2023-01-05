import toml
from box import Box


def _add_list_converts(main_obj, obj: list):
    for arg in obj:
        copy_obj = obj.copy()
        copy_obj.remove(arg)
        main_obj[arg] = copy_obj


class Config(Box):
    IMAGES = ['ktx', 'pvr', 'png', 'jpg', 'sc']
    AUDIO = ['mp3', 'ogg', 'wav', 'flac', 'ape', 'aiff', 'swa', 'psf', 'aac', 'alac', 'dsd']
    MODELS = ['scw', 'glb', 'dae', 'obj', 'fbx']
    CSV = ['decompress', 'compress']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_converts(cls):
        converts = Box()

        _add_list_converts(converts, cls.AUDIO)
        _add_list_converts(converts, cls.MODELS)

        converts.csv = cls.CSV
        converts.sc = ['png']
        converts.png = ['jpg', 'ktx', 'pvr', 'sc']
        converts.jpg = ['png', 'ktx', 'pvr']
        converts.ktx = ['jpg', 'png', 'pvr']
        converts.pvr = ['jpg', 'png', 'ktx']
        converts.scw.append('update')

        return converts


Config = Config(toml.load('config.toml'))
