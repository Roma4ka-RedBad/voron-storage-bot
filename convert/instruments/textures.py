from PIL import Image

from logic_objects.file import FileObject
from .base import Base


class Textures(Base):
    def __init__(self, file: FileObject, process_dir: str, result_dir: str):
        super().__init__(file, process_dir, result_dir)

    async def convert_to(self, to_format: str):
        if self.file.get_format() in ['png', 'jpg'] and to_format in ['png', 'jpg']:
            return await self.to_jpg_or_png(to_format)

    async def to_jpg_or_png(self, to_format: str):
        image = Image.open(self.process_dir + self.file.get_destination(only_shortname=True))
        new_image = image.convert("RGB" if to_format == 'jpg' else "RGBA")
        new_image.save(self.get_new_filename(to_format))
        return self.get_new_filename(to_format)
