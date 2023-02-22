import re
from pathlib import PurePath
from typing import Optional, Union, Iterable

from managers.models.archive.base import BaseArchiveFile
from managers.models.file import File

"""
basic usage example:

tree = Tree()
for file in files:
    tree.add(file)

converts = Converts.match_available_converts(tree.files.values())
"""


class Tree:
    """
    оs.walk - подобный объект для архивов
    """

    def __init__(self):
        self.tree = {0: self.Subfolder(self, 0, 'root_archive', is_root=True)}
        self.files = {}
        self.id = 1
        self.file_id = 0

    def add(self, file_object: Union[File, BaseArchiveFile]) -> Optional["Tree.File"]:
        if isinstance(file_object, File):
            added = self._add_file(path=PurePath(file_object.file_name),
                                   filetype=file_object.file_is,
                                   extension=file_object.filetype_extension or file_object.user_extension
                                   )

        elif isinstance(file_object, BaseArchiveFile):
            added = self._add_file(path=PurePath(file_object.origin.filename),
                                   filetype=file_object.file_is,
                                   extension=file_object.filetype_extension or file_object.user_extension
                                   )
        else:
            return

        file_object.id = added.id
        return added

    def _add_file(self, path: PurePath, filetype, extension) -> "Tree.File":
        past_folder: Tree.Subfolder = self.tree[0]
        for subfolder in path.parts[:-1]:
            if subfolder in past_folder:
                past_folder = past_folder.get_by_name(subfolder)
            else:
                self.tree[self.id] = past_folder = self.Subfolder(self, self.id, subfolder, past_folder)
                self.id += 1

        file = self.File(self, self._get_uniq_file_id(), path.parts[-1], past_folder, filetype, extension)
        past_folder.inside.append(file)
        self.files[file.id] = file

        return file

    def __getitem__(self, item: int):
        if isinstance(item, int):
            return self.tree[item]

        elif isinstance(item, slice):
            result = []
            if item.stop:
                step = item.step or 1
                for i in range(item.start, item.stop, step):
                    result.append(self.tree[i])
                return result
            else:
                return self.tree.values

    def _get_uniq_file_id(self):
        self.file_id += 1
        return self.file_id

    class Subfolder:
        """
        Объект папки
        """

        def __init__(self, owner: "Tree", uniq_id: int, name: str, past=None, is_root=False):
            self.tree = owner
            self.name = name
            self.id = uniq_id
            self.past_folder = past
            self.is_root = is_root  # Только для определения архива как папки
            self.inside: list[Tree.Subfolder | Tree.File] = []  # Объекты Subfolder/File файлов и папок,
            # что находятся в этой папке

            if self.past_folder is not None:
                self.past_folder.inside.append(self)

        def next(self) -> list[int]:
            """
            Возвращает список ид всего, что находится в этой папке
            """
            return [item.id for item in self.inside]

        def back(self) -> "Tree.Subfolder":
            """
            Возвращает Subfolder папки, в которой находится эта папка
            """
            return self.past_folder

        def get_inside(self) -> list["Tree.Subfolder", "Tree.File"]:
            return [i for i in self.inside]

        def get_root(self, with_self=False) -> str:
            """
            Возвращает все папки вплоть до root
            :param with_self: bool Включает эту папку в ответ
            :return: путеподобная строка
            """
            result = []
            subfolder = self
            if not with_self:
                subfolder = self.back()
            result.append(subfolder.name)

            while subfolder.back() is not None:
                result.append(subfolder.name)
                subfolder = self.back()

            return '/'.join(result)

        def get_by_name(self, name) -> Optional["Tree.Subfolder"]:
            for item in self.inside:
                if item.name == name:
                    return item
            return None

        def get_by_id(self, item_id) -> Optional["Tree.Subfolder"]:
            for item in self.inside:
                if item.id == item_id:
                    return item
            return None

        def __eq__(self, other: "Tree.Subfolder") -> bool:
            return self.id == other.id

        def __iter__(self):
            return (item.name for item in self.inside)

        def __repr__(self):
            return str(self.id)

        def __str__(self):
            return f'Subfolder(name={self.name}, id={self.id})'

    class File:
        """
        Объект файла.
        """

        def __init__(self, owner: "Tree", file_id: int, name: str, in_folder: "Tree.Subfolder", file_type: str,
                     ext: str):
            self.tree = owner
            self.name = name
            self.id = file_id
            self.subfolder = in_folder
            self.file_type = file_type
            self.extension = ext
            self.buttons = []

        def back(self) -> "Tree.Subfolder":
            return self.subfolder

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return f'File(name={self.name} id={self.id} file_type={self.file_type} extension={self.extension})'


class Utils:
    ARCHIVE: "Utils.Folder"
    AVAILABLE_TYPES = ['image', 'compressed_image', 'video', 'audio', 'archive', 'font', 'doc', 'json', 'sc', '3d',
                       'shader']  # Берутся из archive.base.AVAILABLE_TYPES

    class Folder:
        # Названия папок могут быть неуникальными. Ид папок всегда уникальны
        def __init__(self, folder_id: int, name: Optional[str] = None):
            self.id = folder_id
            self.name = name

            self.past = None
            self.next = None

        def __truediv__(self, other: Union["Utils.Folder", "Utils.File"]) -> "Utils.File":
            self.next = other
            other.past = self

            return other

    class File:
        def __init__(self, file_type: Optional[str | Iterable[str]] = None,
                     file_ext: Optional[str] = None,
                     name: Optional[str] = None):
            self.file_type = file_type
            self.file_ext = file_ext
            self.name = name

            self.past: Optional[Utils.Folder] = None

            if not file_ext and not file_type:
                raise SystemExit('Тип файла или его расширение должны быть заполнены!')

            if isinstance(self.file_type, str):
                self.file_type = [self.file_type]

        def get_root(self) -> Optional["Utils.Folder"]:
            subfolder = self.past
            if subfolder is not None:
                while subfolder.past is not None:
                    subfolder = subfolder.past

            return subfolder

        def get_folder_ids(self) -> list[int]:
            temp = []
            folder = self.get_root()
            if folder is not None:
                temp.append(folder.id)
                while not isinstance(folder.next, Utils.File):
                    folder = folder.next
                    temp.append(folder.id)

            return [None] if not temp else temp

    class Optional:
        def __init__(self, *objects: Union["Utils.File", "Utils.Limit"], warning: Optional[str] = ''):
            """
            Делает наличие файла необязательным.
            :param objects: объекты файлов.
            :param warning: Текст предупреждения, если этот паттерн не будет найден, иначе ''
            """
            self.objects = objects
            self.warning_text = warning

            if any(isinstance(obj, Utils.Optional) for obj in self.objects):
                raise SystemExit("Не имеет смысла ставить Optional[Optional[...]], это потом сложновато парсить. "
                                 "Убери Optional из элементов (error from class Utils.Optional)")
            if any(isinstance(obj, Utils.Folder) for obj in self.objects):
                raise SystemExit("Элементами должны быть объекты файлов! (error from class Utils.Optional)")

    class Limit:
        def __init__(self, *objects: "Utils.File", minimum: int = 1):
            """
            Устанавливает лимит для поиска файлов. Если будут найдены несколько файлов по этому шаблону - они все
            будут использованы. Шаблон задаётся регулярным выражением в имени файла.
            :param args: объекты папок и файла.
            :param minimum: положительное число больше 0
            """

            self.objects = objects
            self.minimum = minimum

            if any(isinstance(obj, Utils.Limit) for obj in self.objects):
                raise SystemExit("Хуйню какую то сделал блять. Как ты мне предлагаешь лимит в лимите обработать?")
            if not all(isinstance(obj, Utils.File) for obj in self.objects):
                raise SystemExit("Элементами должны быть объекты файлов! (error from class Utils.Limit)")
            if not isinstance(minimum, int) or minimum < 0:
                raise SystemExit("Минимум должен быть положительным целым числом!")


class MatchObject:
    def __init__(self, method):
        self.BUTTONS = method.BUTTONS
        self.CONDITIONS = self.Conditions(method.CONDITIONS)

        self.__name__ = method.__name__

    def create_storage(self):
        return СукаБлятьРомаПомогиЭтоНазвать(self)

    class Conditions:
        def __init__(self, conditions: list[Utils.File, Utils.Optional, Utils.Limit]):
            self.prepared: dict = {}
            self.conditions: list["MatchObject.Conditions.SingleCondition"] = []
            self._uniq_id: int = 0

            for num, cond in enumerate(conditions):
                self.prepared[num] = {'optional': False, 'files': []}
                self._deep(num, cond)

            id_patterns = set(cond.folder_ids_pattern[0] for cond in self.conditions)
            if len(id_patterns) != 1 or None in id_patterns:
                for _ in range(len(self.conditions)):
                    if self.conditions[_].folder_ids_pattern[0] is None:
                        self.conditions[_].folder_ids_pattern[0] = -1
                    else:
                        self.conditions[_].folder_ids_pattern.insert(0, -1)

        def _deep(self, cond_number: int, obj: Union[Utils.File, Utils.Limit, Utils.Optional],
                  _limit_file: bool = False):
            if isinstance(obj, Utils.Optional):
                self.prepared[cond_number]['warning'] = str(obj.warning_text)
                for obj in obj.objects:
                    self.prepared[cond_number]['optional'] = True
                    self._deep(cond_number, obj)

            elif isinstance(obj, Utils.Limit):
                _limit = []
                for file in obj.objects:
                    _limit.append(self._deep(cond_number, file, _limit_file=True))

                self.prepared[cond_number]['files'].append(
                        {'type': 'limit', 'metadata': (obj.minimum,), 'ids': _limit})

            elif isinstance(obj, Utils.File):
                cond = self.SingleCondition(obj, self._uniq_id, limit=_limit_file)
                self.conditions.append(cond)
                self._uniq_id += 1

                if _limit_file:
                    return cond.id
                self.prepared[cond_number]['files'].append(
                        {'type': 'file', 'metadata': (), 'ids': cond.id})

        class SingleCondition:
            def __init__(self, file: Utils.File, uniq_id: int, limit: Optional[bool] = False):
                self.id = uniq_id
                self.file_pattern = file
                self.folder_ids_pattern = self.file_pattern.get_folder_ids()
                self.limit = limit

            def match(self, compare_file: Tree.File) -> Optional[tuple[int, str, str, Tree.File]]:
                """
                Сравнить файл на совпадение с шаблоном файла.
                :param compare_file: объект файла.
                :return: при удачном совпадении: ид условия, общий корень, общий паттерн имени (типа "loading",
                "background_basic"), ид файла
                """
                name = ''

                if not (root := self.get_root(compare_file)):
                    return

                if self.file_pattern.file_type:
                    if compare_file.file_type not in self.file_pattern.file_type:
                        return

                if self.file_pattern.file_ext:
                    if not compare_file.name.endswith(self.file_pattern.file_ext):
                        return

                if self.file_pattern.name:
                    if not re.fullmatch(str(self.file_pattern.name).replace('{name}', '.*'), str(compare_file.name)):
                        return
                    else:
                        name = self.get_optional_name(self.file_pattern.name, compare_file.name)

                return self.id, root, name, compare_file

            @staticmethod
            def get_optional_name(pattern_name, file_name) -> str:
                if '{name}' not in pattern_name:
                    return ''

                pattern = pattern_name.split('{name}')
                result = str(file_name)

                if pattern[0]:
                    result = re.split(pattern[0], result)[-1]
                if pattern[1]:
                    result = re.split(pattern[1], result)[0]

                return result

            def get_root(self, file: Tree.File):
                past = None
                for count in range(len(self.folder_ids_pattern)):
                    past = file.back()
                    if past is None:
                        return
                return past.get_root(with_self=True)


class СукаБлятьРомаПомогиЭтоНазвать:
    def __init__(self, match_object: MatchObject):
        self.match_object = match_object
        self.storage: list[dict] = []

    def get_result(self):
        result = {}
        if len(self.match_object.CONDITIONS.conditions) == 1:
            for file in self.storage:
                for button in self.match_object.BUTTONS:
                    if button not in result:
                        result[button] = []
                    file['conditions'][0]['files'][0].buttons.append(button)
                    result[button].append(file['conditions'][0]['files'][0].id)

        else:
            for file in self.storage:
                pre_result = {'file_ids': [], 'warnings': []}
                folders = {}
                for num, cond in self.match_object.CONDITIONS.prepared.items():
                    temp, validate = [], []
                    folders[num] = {}

                    for file_ in cond['files']:
                        if file_['type'] == 'limit':
                            another_temporary = []
                            for _id in file_['ids']:
                                folders[num][_id] = []
                                for f in file['conditions'][_id]['files']:
                                    another_temporary.append(f.id)
                                    folders[num][_id].append(f)

                            if len(another_temporary) < file_['metadata'][0] and not cond['optional']:
                                validate.append(False)
                                continue

                            temp.extend(another_temporary)
                            validate.append(True)

                        elif file_['type'] == 'file':
                            if is_matched := file['conditions'][file_['ids']]['matched']:
                                temp.extend(file['conditions'][file_['ids']]['files'][0])
                                folders[num][file_['ids']].append(file['conditions'][file_['ids']]['files'][0])
                            validate.append(is_matched)

                    if all(validate):
                        pre_result['file_ids'].extend(temp)
                        continue

                    if cond['optional']:
                        if any(validate):
                            pre_result['file_ids'].extend(temp)
                            continue
                        else:
                            pre_result['warnings'].append(cond['warning'])
                            continue

                    pre_result = {}
                    break

                if not self.check_folders(folders):
                    continue

                for button in self.match_object.BUTTONS:
                    if button not in result:
                        result[button] = []
                    result[button].append(pre_result)

        return result

    def check_folders(self, folders: dict) -> Optional[dict]:
        temp = {}
        for cond in folders.values():
            for _id in cond:
                pattern = self.match_object.CONDITIONS.conditions[_id].folder_ids_pattern[::-1]
                for file in cond[_id]:
                    subfolder = file.back()
                    for folder_id in pattern:
                        if (folder := temp.get(folder_id)) is not None:
                            if subfolder != folder:
                                return None
                        else:
                            temp[folder_id] = subfolder

                        subfolder = subfolder.back()

        return temp

    def check_file(self, file: Tree.File):
        for cond in self.match_object.CONDITIONS.conditions:
            if match := cond.match(file):
                matched = False
                for num in range(len(self.storage)):
                    # продолжить, если условие в этом паттерне уже занято и оно не является лимитом
                    if self.storage[num]['conditions'][match[0]]['matched']:
                        if not self.match_object.CONDITIONS.conditions[match[0]].limit:
                            continue

                    # Если совпадает корень
                    if self.storage[num]['root'] == match[1]:
                        # если совпадает паттерн имени или он не определён
                        if self.storage[num]['name'] == match[2] or self.storage[num]['name'] == '':
                            if self.storage[num]['name'] == '':
                                self.storage[num]['name'] = match[2]

                            self.storage[num]['conditions'][match[0]]['files'].append(match[3])
                            self.storage[num]['conditions'][match[0]]['matched'] = True
                            matched = True
                            break
                if matched:
                    continue
                self.add(*match)

    def add(self, condition_id: int, root: str, name: Optional[str] = '', file_id: int = 0):
        self.storage.append({'name': name,
                             'root': root,
                             'conditions': {num: {'matched': False, 'files': []} for num in range(len(
                                     self.match_object.CONDITIONS.conditions))}})
        self.storage[-1]['conditions'][condition_id]['matched'] = True
        self.storage[-1]['conditions'][condition_id]['files'].append(file_id)

    def __repr__(self):
        return self.match_object.__name__


class Converts:
    @classmethod
    def init(cls):
        for method in cls.__all__():
            if 'BUTTONS' not in dir(method):
                raise SystemExit(f'Массив возвращаемых кнопок не определен в {method.__name__}')
            elif isinstance(method.BUTTONS, Iterable):
                if not all(isinstance(button, str) for button in method.BUTTONS):
                    raise SystemExit(f'Все кнопки должны быть строками! (Error from {method.__name__})')
            else:
                method.BUTTONS = [str(method.BUTTONS)]

            if 'CONDITIONS' not in dir(method):
                raise SystemExit(f'Массив с условием для {method.__name__} не определен!')
            elif isinstance(method.CONDITIONS, Iterable):
                if not all(isinstance(item, (Utils.Folder, Utils.File, Utils.Optional, Utils.Limit)) for item in
                           method.CONDITIONS):
                    raise SystemExit('Условие должно быть массивом объектов из Utils!')
            elif isinstance(method.CONDITIONS, (Utils.Folder, Utils.File, Utils.Optional, Utils.Limit)):
                method.CONDITIONS = [method.CONDITIONS]
            else:
                raise SystemExit('Условие должно быть массивом объектов из Utils!')

            exec(f'{method.__qualname__} = MatchObject(method)')

    @classmethod
    def __all__(cls):
        return [
            cls.Image,
            cls.ToSC,
            cls.FromSC,
            cls.Audio,
            cls.CSV,
            cls.Models,
        ]

    @classmethod
    def __repr__(cls):
        return cls.__all__()

    @classmethod
    def __iter__(cls):
        return iter(cls.__all__())

    @classmethod
    def match_available_converts(cls, files: list[Tree.File], *methods: Optional):
        """
        :param files: Tree.files
        :param methods: методы из Converts.__all__()
        :return: {'button': {'file_ids': [int | tuple[int]], 'warnings': [str]}, ...}
        """
        if not methods:
            methods = cls.__all__()

        methods = [method.create_storage() for method in methods]
        for file in files:
            for method in methods:
                method.check_file(file)

        result = {}
        for method in methods:
            if res := method.get_result():
                for button, files in res.items():
                    if button not in result:
                        result[button] = set(files)
                    else:
                        result[button].update(files)

        for button in result:
            result[button] = sorted(result[button])

        return result

    class Info:
        BUTTONS = []  # Массив кнопок, который вернется при успешном совпадении шаблона
        CONDITIONS = []  # Массив путей типа /root/folder/file, где root - папка с одинаковыми ид.
        # (это значит, что все файлы должны лежать в одной папке, в конечном счете это будет сам архив)
        # Если указано несколько файлов (например для sc2tex), то root папкой считается первая папка (если ид одинаковы)
        # или же предыдущая папка, в том числе и сам архив
        # Папки необязательно указывать, если они не важны

    class Image:
        BUTTONS = ['png', 'ktx', 'pvr', 'jpg']
        CONDITIONS = [
            Utils.File(file_type=('image', 'compressed_image'))
        ]

    class ToSC:
        BUTTONS = ['sc']
        CONDITIONS = [
            Utils.Limit(Utils.Folder(1) / Utils.File(file_type='image', name=r'{name}_tex_*\.png'),
                        minimum=1),
            Utils.Optional(Utils.Folder(1) / Utils.File(file_type='image', name=r'{name}_tex\.json'),
                           warning='Json файл не найден. Приложите его для более точной конвертации')
        ]

    class FromSC:
        BUTTONS = ['png']
        CONDITIONS = [
            Utils.File(file_type='sc')
        ]

    class Audio:
        BUTTONS = ['ogg', 'mp3', 'waw']
        CONDITIONS = [
            Utils.File(file_type='audio')
        ]

    class Models:
        BUTTONS = ['scw', 'glb', 'dae', 'obj', 'fbx']
        CONDITIONS = [
            Utils.File(file_type='3d')
        ]

    class CSV:
        BUTTONS = ['decompress', 'compress']
        CONDITIONS = [
            Utils.File(file_ext='.csv')
        ]


Utils.ARCHIVE = Utils.Folder(0, 'root_archive')
Converts.init()
