import os
import shutil
import random

from typing import List

from logic_objects import FileObject, ArchiveObject
from convert.instruments.textures import Textures


class ConvertManager:
    def __init__(self, config):
        self.config = config

    async def start_tool(self, files: List[FileObject] | FileObject, process_dir: str, to_format: str, metadata: list):
        result_file = None
        if type(files) is list:
            result_file = ArchiveObject(
                FileObject.create(process_dir + 'archive.zip', files[0].messenger, files[0].config),
                "w", "zip"
            )

        if to_format in self.config.CONVERTS['2D']:
            if result_file:
                for file in files:
                    process = Textures(file, process_dir)
                    if result_dir := await process.convert_to(to_format):
                        result_file.write(result_dir)
                result_file = result_file.file.get_destionation()
            else:
                process = Textures(files, process_dir)
                result_file = await process.convert_to(to_format)

        return result_file

    async def convert(self, file: FileObject, to_format: str, metadata: list):
        process_dir = file.get_destionation(only_dir=True) + f'process_{random.randint(0, 1000000)}/'
        files = []

        os.makedirs(process_dir)
        os.makedirs(process_dir + 'new_files')

        if archive := file.get_archive():
            if file.archive_file != file.get_destionation(only_name=True):
                extract_file = archive.get_file_by_name(file.archive_file)
                extracted_dir = extract_file.extract(process_dir)
                shutil._samefile = lambda *a, **b: False
                files = FileObject(path=shutil.copy(extracted_dir, process_dir + extract_file.get_shortname()),
                                   messenger=file.messenger, config=file.config)
            else:
                for extract_file in archive.get_files():
                    extracted_dir = extract_file.extract(process_dir)
                    files.append(FileObject(path=extracted_dir,
                                            messenger=file.messenger, config=file.config))
        else:
            files = file
            shutil.copy(file.get_destionation(), process_dir + file.get_destionation(only_name=True))

        result = await self.start_tool(files, process_dir, to_format, metadata)
        return result, process_dir
