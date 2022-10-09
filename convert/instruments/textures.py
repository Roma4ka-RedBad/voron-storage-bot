from PIL import Image

from logic_objects.file import FileObject


class Textures:
    def __init__(self, file: FileObject, process_dir: str):
        self.file = file
        self.process_dir = process_dir

    def get_new_filename(self, to_format: str):
        return f"{self.file.get_destionation(only_shortname=True).split('.')[0]}_new.{to_format}"

    async def convert_to(self, to_format: str):
        if self.file.get_format() in ['png', 'jpg'] and to_format in ['png', 'jpg']:
            return await self.to_jpg_or_png(to_format)

    async def to_jpg_or_png(self, to_format: str):
        image = Image.open(self.process_dir + self.file.get_destionation(only_shortname=True))
        new_image = image.convert("RGB" if to_format == 'jpg' else "RGBA")
        new_image.save(self.process_dir + self.get_new_filename(to_format))
        return self.process_dir + self.get_new_filename(to_format)
