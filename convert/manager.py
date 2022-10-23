import os
import shutil
import random

from zipfile import ZipFile

from logic_objects import FileObject
from convert.instruments.textures import Textures
from convert.instruments.audios import Audios


class ConvertManager:
    def __init__(self, config):
        self.config = config

    async def start_tool(
            self,
            file: FileObject,
            process_dir: str,
            result_dir: str,
            to_format: str,
            data=None):
        # так пичарм говорит делать вместо data={}
        if data is None:
            data = {}

        if to_format in self.config.CONVERTS['2D']:
            process = Textures(file, process_dir, result_dir)

        elif to_format in self.config.CONVERTS['AUDIO']:
            process = Audios(file, process_dir, result_dir, **data)

        else:
            return None, None

        return await process.convert_to(to_format)

    async def convert(self, file: FileObject, to_format: str, data: dict):
        main_dir = file.get_destination(only_dir=True)
        process_dir = main_dir + f'process_{random.randint(0, 1000000)}/'
        result_dir = main_dir + f'result/'
        os.makedirs(process_dir)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        if archive := file.get_archive():
            if file.archive_file != file.get_destination(only_shortname=True):
                extract_file = archive.get_file_by_name(file.archive_file)
                extracted_dir = extract_file.extract(process_dir)
                file = FileObject(
                    name=shutil.copy(extracted_dir, process_dir + extract_file.get_shortname()),
                    messenger=file.messenger, config=file.config)
            else:
                print("Ну пока...")
                return None, None
        else:
            shutil.copy(
                file.get_destination(), process_dir + file.get_destination(
                    only_shortname=True))

        result = await self.start_tool(file, process_dir, result_dir, to_format, data)
        return result, result_dir

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
