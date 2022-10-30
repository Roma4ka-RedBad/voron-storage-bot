import os
import platform
from pathlib import Path

from PIL import Image

from logic_objects.file import FileObject
from .base import Base


class Textures(Base):
    def __init__(self, file: FileObject, result_dir: str):
        super().__init__(file, result_dir)
        self.pvrtextool = Path("convert/instruments/pvrtextools/" +
                                       'pvrtextool.exe' if platform.system() == 'Windows' else 'pvrtextool')

    async def convert_to(self, to_format: str):
        if self.file.path.suffix[1:] in ['png', 'jpg'] and to_format in ['png', 'jpg']:
            return await self.to_jpg_or_png(to_format)
        elif self.file.path.suffix[1:] in ['png', 'jpg'] and to_format in ['ktx', 'pvr']:
            return await self.to_ktx_or_pvr_or_back(to_format)
        elif self.file.path.suffix[1:] in ['ktx', 'pvr'] and to_format in ['png', 'jpg']:
            return await self.to_ktx_or_pvr_or_back(to_format)

    async def to_jpg_or_png(self, to_format: str):
        image = Image.open(self.file.path)
        new_image = image.convert("RGB" if to_format == 'jpg' else "RGBA")
        new_image.save(self.get_new_filename(to_format))
        return self.get_new_filename(to_format)

    async def to_ktx_or_pvr_or_back(self, to_format: str):
        try:
            argument = '-o' if to_format in ['ktx', 'pvr'] else '-d'
            if argument == '-d':
                encode_format = "R8G8B8A8" if to_format == 'png' else "R8G8B8"
            else:
                encode_format = "ETC1" if to_format == 'ktx' else 'PVRTC1_2_RGB'

            print(
                f"{self.pvrtextool} -i {self.file.path} {argument} {self.get_new_filename(to_format)} -f {encode_format}")
            os.system(
                f"{self.pvrtextool} -i {self.file.path} {argument} {self.get_new_filename(to_format)} -f {encode_format}")
            return self.get_new_filename(to_format)
        except:
            pass
