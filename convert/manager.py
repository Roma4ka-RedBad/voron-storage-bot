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

    async def start_tool(self, files: List[FileObject], process_dir: str, result_dir: str, to_format: str,
                         metadata: Metadata):
        result = []

        for file in files:
            if to_format in self.config.CONVERTS['2D']:
                process = Textures(file, process_dir, result_dir)
                if process := await process.convert_to(to_format):
                    result.append(process)

            elif to_format in self.config.CONVERTS['AUDIO']:
                process = Audios(file, process_dir, result_dir, metadata)
                if process := await process.convert_to(to_format):
                    result.append(process)

        return result[0] if len(result) == 1 else result

    async def convert(self, file: FileObject, to_format: str, metadata: Metadata):
        main_dir = file.get_destination(only_dir=True)
        process_dir = main_dir + f'process_{random.randint(0, 1000000)}/'
        result_dir = main_dir + f'result/'
        files = []

        shutil._samefile = lambda *a, **b: False
        os.makedirs(process_dir)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        if archive := file.get_archive():
            if file.archive_file != file.get_destination(only_name=True):
                extract_file = archive.get_file_by_name(file.archive_file)
                extracted_dir = shutil.copy(extract_file.extract(process_dir),
                                            process_dir + extract_file.get_shortname())
                files.append(FileObject(path=extracted_dir, messenger=file.messenger, config=file.config))
            else:
                for extract_file in archive.get_files():
                    if not extract_file.is_dir():
                        extracted_dir = shutil.copy(extract_file.extract(process_dir),
                                                    process_dir + extract_file.get_shortname())
                        files.append(FileObject(path=extracted_dir, messenger=file.messenger, config=file.config))
        else:
            shutil.copy(file.get_destination(), process_dir + file.get_destination(only_name=True))
            files.append(file)

        result = await self.start_tool(files, process_dir, result_dir, to_format, metadata)
        return result, process_dir
