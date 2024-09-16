import os
import random

from typing import List
from logic_objects import FileObject, Metadata, QueueFileObject, Config

from managers.instruments.textures import Textures
from managers.instruments.audios import Audios
from managers.instruments.csv import Csv
from managers.instruments.models import Models


class ConvertManager:
    def __init__(self, queue_manager):
        self.queue = queue_manager

    async def select_tool(self, files: List[FileObject], result_dir, to_format: str, metadata: Metadata):
        result = []

        for file in files:
            if to_format == 'sc' and file.path.suffix[1:] == 'png':
                process = Textures(files, result_dir)
                result.append(QueueFileObject(target=process.convert_to, arguments=(to_format,)))
                break

            elif to_format in Config.IMAGES and file.path.suffix[1:] in Config.IMAGES:
                process = Textures(file, result_dir)
                result.append(QueueFileObject(target=process.convert_to, arguments=(to_format,)))

            elif to_format in Config.AUDIO and file.path.suffix[1:] in Config.AUDIO:
                process = Audios(file, result_dir, metadata)
                result.append(QueueFileObject(target=process.convert_to, arguments=(to_format,)))

            elif to_format in Config.CSV and file.path.suffix[1:] == 'csv':
                process = Csv(file, result_dir)
                result.append(QueueFileObject(target=process.convert_to, arguments=(to_format,)))

            elif to_format in Config.MODELS and file.path.suffix[1:] in Config.MODELS:
                process = Models(file, result_dir)
                result.append(QueueFileObject(target=process.convert_to, arguments=(to_format,)))

        result = await self.queue.wait_for_convert(result)

        return [{'path': obj.path_result, 'tid': obj.tid} for obj in result]

    async def convert(self, raw_files: List[FileObject], to_format: str, metadata: Metadata):
        process_dir = raw_files[0].path.parent / f'process_{random.randint(0, 1000000)}/'
        result_dir = raw_files[0].path.parent / 'result'
        files = []
        raw_files = [file for file in raw_files if file.path.exists()]
        if not raw_files:
            return None, None

        only_one_archive = [True for obj in raw_files if obj.get_archive()].count(True) == 1

        os.makedirs(process_dir)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        for file in raw_files:
            if archive := file.get_archive():
                if file.target_file is not None and only_one_archive:
                    extract_file = archive.get_file_by_name(file.target_file).extract(process_dir)
                    files.append(extract_file.copy_to(process_dir))
                else:
                    for extract_file in archive.get_files():
                        if not extract_file.is_dir():
                            files.append(extract_file.extract(process_dir).copy_to(process_dir))
            else:
                files.append(file.copy_to(process_dir))

        result = await self.select_tool(files, result_dir, to_format, metadata)

        return result, process_dir