import os
import shutil
import random

from typing import List
from logic_objects import FileObject, Metadata

from convert.instruments.textures import Textures
from convert.instruments.audios import Audios


class ConvertManager:
    def __init__(self, config):
        self.config = config

    async def start_tool(self, files: List[FileObject], result_dir, to_format: str, metadata: Metadata):
        result = []

        for file in files:
            if to_format in self.config.CONVERTS['2D']:
                process = Textures(file, result_dir)
                if process := await process.convert_to(to_format):
                    result.append(process)

            elif to_format in self.config.CONVERTS['AUDIO']:
                process = Audios(file, result_dir, metadata)
                if process := await process.convert_to(to_format):
                    result.append(process)

        return result[0] if len(result) == 1 else result

    async def convert(self, file: FileObject, to_format: str, metadata: Metadata):
        process_dir = file.path.parent / f'process_{random.randint(0, 1000000)}/'
        result_dir = file.path.parent / 'result'
        files = []

        shutil._samefile = lambda *a, **b: False
        os.makedirs(process_dir)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        if archive := file.get_archive():
            if file.target_file != None:
                extract_file = archive.get_file_by_name(file.target_file).extract(process_dir)
                files.append(extract_file.copy_to(process_dir))
            else:
                for extract_file in archive.get_files():
                    if not extract_file.is_dir():
                        files.append(extract_file.extract(process_dir).copy_to(process_dir))
        else:
            files.append(file.copy_to(process_dir))

        result = await self.start_tool(files, result_dir, to_format, metadata)
        return result, process_dir
