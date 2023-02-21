import functools
import sys
from json import load
from pathlib import Path, PurePath
from typing import Literal, IO, BinaryIO

import aiohttp
from filetype import guess
from filetype.types import IMAGE, VIDEO, AUDIO, ARCHIVE, FONT, DOCUMENT
from sc_compression.signatures import Signatures, get_signature

AVAILABLE_TYPES = ['image', 'compressed_image', 'video', 'audio', 'archive', 'font', 'doc', 'json', 'sc', '3d',
                   'shader']

filetypes = {
    IMAGE: 'image',
    VIDEO: 'video',
    AUDIO: 'audio',
    ARCHIVE: 'archive',
    FONT: 'font',
    DOCUMENT: 'doc'
}


class BytesIO:
    """
    Особенность этого класса в том, что он не закрывает файловый объект, а перемещает курсор в начало файла.
    Создан преимущественно для работы с файлами в архивах, чтобы их не распаковывать.
    Поддерживает with ... as ...
    Поддерживает срезы (bytes_io[2, 10, 5])
    """

    def __init__(self, bytes_io: BinaryIO):
        self.bytes_io = bytes_io

    def read(self, count: int = 0) -> bytes:
        """
        Читает n байт
        """
        if count:
            result = self.__read__(count)
        else:
            result = self.__read__()
        self.bytes_io.seek(0)

        return result

    def open(self):
        return self.bytes_io

    def close(self):
        self.bytes_io.seek(0)

    def __read__(self, count: int = 0):
        # не вызывает метод seek
        if count:
            return self.bytes_io.read(count)
        else:
            return self.bytes_io.read()

    def __enter__(self):
        return self.bytes_io

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bytes_io.seek(0)

    def __repr__(self):
        return self.bytes_io

    def __getitem__(self, item: int):
        result = None
        if isinstance(item, int):
            result = self.__read__(item)

        elif isinstance(item, slice):
            result = b''
            if item.start:
                self.__read__(item.start)
            if item.stop:
                step = item.step or 1
                while item.start <= item.stop:
                    result += self.__read__(1)
                    self.__read__(step - 1)
                    item.start += step
            else:
                result = self.__read__()
        self.bytes_io.seek(0)

        return result


async def async_request(url: str, return_type: str, data=None):
    async with aiohttp.ClientSession() as session:
        if data:
            async with session.post(url, json=data) as resp:
                if resp.status == 200:
                    if return_type == 'bytes':
                        return await resp.content.read()
                    elif return_type == 'json':
                        return await resp.json()
                    elif return_type == 'text':
                        return await resp.text()
        else:
            async with session.get(url) as resp:
                if resp.status == 200:
                    if return_type == 'bytes':
                        return await resp.content.read()
                    elif return_type == 'json':
                        return await resp.json()
                    elif return_type == 'text':
                        return await resp.text()


def file_writer(file_name: str, data: bytes | str, mode: Literal['w', 'wb', 'a'] = "wb") -> str:
    with open(file_name, mode) as file:
        file.write(data)

    return file_name


def super_(*subclasses):
    """Кастомный super, позволяющий наследовать от нужного класса.

    Аргументы функции это класс(ы), от которых нужно наследовать метод.

    Пример использования:

    class one:
        ...
    class two:
        ...
    class example(one, two):
        def __init__(self):
            super_(two)
    """

    frame = sys._getframe(1)  # завались сука интерпретатор ебаный
    base_class = frame.f_locals[frame.f_code.co_varnames[0]]

    if subclasses:
        base_class._mro = []
        for arg in subclasses:
            base_class.mro_.append(arg)
        for arg in subclasses:
            base_class.mro_.extend([*arg.mro[1:]])

    if '_mro' in dir(base_class):
        mro = base_class.mro_
    else:
        mro = type(base_class).mro

    class Proxy:
        def __getattribute__(self, attribute_name):
            for superclass in mro:
                try:
                    method = getattr(superclass, attribute_name).get(base_class)
                except AttributeError:
                    continue

                # просто кек чтобы не было ObJeCt Is NoT CaLlAbLe идИ НАхУйЙй!!
                if not callable(method):
                    return method

                @functools.wraps(method)
                def wrapper(*args, **kwargs):
                    return method(*args, **kwargs)

                return wrapper

            raise AttributeError(f"'super_' object has no attribute '{attribute_name}'")

    return Proxy()


def guess_file_format(path: Path | PurePath, bytes_io: IO | BinaryIO | BytesIO) -> tuple:
    """
    :param path: путь до файла.
    :param bytes_io: файловый объект, открытый для чтения в бинарном режиме.
    :return: tuple(тип файла (по заголовку), расширение файла, тип файла (по условиям))
    """

    if path.is_dir():
        return None, None, 'directory'

    if not isinstance(bytes_io, BytesIO):
        bytes_io = BytesIO(bytes_io)
    header = bytes_io.read(32)

    filetype = guess(bytes_io.bytes_io)
    extension = filetype.EXTENSION if filetype is not None else None

    if filetype == 'jpg':
        return filetype, extension, 'compressed_image'

    elif header[:4] == b'\xabKTX':
        return filetype, 'ktx', 'image'

    elif header[:4] == b'SC3D':
        return filetype, 'scw', '3d'

    elif get_signature(header) == Signatures.SC:
        return filetype, 'sc', 'sc'

    elif header[:4] == b'glTF':
        return filetype, 'glb', '3d'

    for f_type in filetypes:
        if filetype in f_type:
            return filetype, extension, filetypes[f_type]

    try:
        if load(bytes_io):
            return filetype, 'json', 'json'
    except (ValueError, TypeError):
        pass

    if path.name.endswith(('.vert.shader', '.frag.shader')):
        return filetype, '.'.join(path.name.split('.')[-2:-1]), 'shader'

    return filetype, extension, None
