import os
import shutil
import random

from typing import List
from logic_objects import FileObject, Metadata, QueueFileObject

from convert.instruments.textures import Textures
from convert.instruments.audios import Audios
from convert.queues import QueueManager


class ConvertManager:
    def __init__(self, config):
        self.config = config
        self.queue = QueueManager()

    async def select_tool(
            self, files: List[FileObject], result_dir, to_format: str, metadata: Metadata) -> List[str]:
        result = []

        for file in files:
            if to_format in self.config.CONVERTS['2D']:
                process = Textures(file, result_dir)
                result.append(QueueFileObject(target=process.convert_to,
                                              arguments=(to_format, )))

            elif to_format in self.config.CONVERTS['AUDIO']:
                process = Audios(file, result_dir, metadata)
                result.append(QueueFileObject(target=process.convert_to,
                                              arguments=(to_format, )))

        result = await self.queue.wait_for_convert(result)

        return [obj.path_result for obj in result]

    async def convert(self, raw_files: List[FileObject], to_format: str, metadata: Metadata):
        process_dir = raw_files[0].path.parent / f'process_{random.randint(0, 1000000)}/'
        result_dir = raw_files[0].path.parent / 'result'
        files = []
        only_one_archive = [obj.get_archive() for obj in raw_files].count(True) == 1
        shutil._samefile = lambda *a, **b: False
        os.makedirs(process_dir)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        for file in raw_files:
            if archive := file.get_archive():
                # я допускаю возможность кидать несколько архивов на вк, например, для премиум
                # юзеров, но скорее всего, тогда конвертация будет только в один формат и я не
                # буду передавать target_file. Если такое произойдет, я сделал проверку на то,
                # чтобы был только один архив в файлах.
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
        # result это список путей на результат конвертации каждого файла

        return result, process_dir
