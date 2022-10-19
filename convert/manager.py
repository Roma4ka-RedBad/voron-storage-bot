import os
import shutil
import random

from logic_objects import FileObject
from convert.instruments.textures import Textures


class ConvertManager:
    def __init__(self, config):
        self.config = config

    async def start_tool(self, file: FileObject, process_dir: str, to_format: str):
        if to_format in self.config.CONVERTS['2D']:
            process = Textures(file, process_dir)
            return await process.convert_to(to_format)

    async def convert(self, file: FileObject, to_format: str):
        process_dir = file.get_destionation(only_dir=True) + f'process_{random.randint(0, 1000000)}/'
        os.makedirs(process_dir)
        os.makedirs(process_dir + 'new_files')

        if archive := file.get_archive():
            if file.archive_file != file.get_destionation(only_shortname=True):
                extract_file = archive.get_file_by_name(file.archive_file)
                extracted_dir = extract_file.extract(process_dir)
                file = FileObject(name=shutil.copy(extracted_dir, process_dir + extract_file.get_shortname()),
                                  messenger=file.messenger, config=file.config)
            else:
                print("Ну пока...")
                return None, None
        else:
            shutil.copy(file.get_destionation(), process_dir + file.get_destionation(only_shortname=True))

        result = await self.start_tool(file, process_dir, to_format)
        return result, process_dir
