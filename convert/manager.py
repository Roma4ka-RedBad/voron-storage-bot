import os
import shutil
import random

from typing import List
from zipfile import ZipFile
from logic_objects import FileObject, ArchiveObject

from convert.instruments.textures import Textures
from convert.instruments.audios import Audios


class ConvertManager:
    def __init__(self, config):
        self.config = config

    async def start_tool(self, files: List[FileObject] | FileObject, process_dir: str, result_dir: str, to_format: str, metadata: dict):
        result_file = None
        if type(files) is list:
            result_file = ArchiveObject(
                FileObject.create(process_dir + 'archive.zip', files[0].messenger, files[0].config),
                "w", "zip"
            )

        if to_format in self.config.CONVERTS['2D']:
            if result_file:
                for file in files:
                    process = Textures(file, process_dir, result_dir)
                    if result_dir := await process.convert_to(to_format):
                        result_file.write(result_dir)
                result_file = result_file.file.get_destination()
            else:
                process = Textures(files, process_dir, result_dir)
                result_file = await process.convert_to(to_format)
                
        elif to_format in self.config.CONVERTS['AUDIO']:
            process = Audios(files, process_dir, result_dir, **metadata)
            result_file = process.convert_to(to_format)

        return result_file

    async def convert(self, file: FileObject, to_format: str, metadata: dict):
        main_dir = file.get_destination(only_dir=True)
        process_dir = main_dir + f'process_{random.randint(0, 1000000)}/'
        result_dir = main_dir + f'result/'
        files = []

        os.makedirs(process_dir)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        if archive := file.get_archive():
            if file.archive_file != file.get_destination(only_name=True):
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
            shutil.copy(file.get_destination(), process_dir + file.get_destination(only_name=True))

        result = await self.start_tool(files, process_dir, result_dir, to_format, metadata)
        return result, process_dir

    @staticmethod
    async def compress_to_archive(path: str, archive_name: str = None, archive_path: str = None):
        if not archive_name:
            archive_name = path.split('/')[-1] + '.zip'

        if not archive_path:
            archive_path = '/'.join(path.split('/')[:-1])

        with ZipFile(f'{archive_path}/{archive_name}', 'w', compresslevel=10) as archive:
            for folder, subfolder, files in os.walk(path):
                for file in files:
                    archive.write(
                        os.path.join(folder, file),
                        os.path.join(folder.replace(path, ''), file))

        return f'{archive_path}/{archive_name}'
