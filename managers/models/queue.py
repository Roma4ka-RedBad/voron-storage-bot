import asyncio
import warnings
import traceback

from multiprocessing import Process, Pipe, cpu_count
from collections import OrderedDict
from collections.abc import Callable, Coroutine
from pydantic import BaseModel

warnings.filterwarnings("ignore", category=RuntimeWarning)


# Мне лень распихивать что-то по файлам. Сам распихаешь!
class QueueFileObject(BaseModel):
    target: Callable[[...], str] | Coroutine = None
    arguments: tuple = None
    priory: tuple[int] = (0, 3)  # system call, 0 is the highest priory
    done: bool = False  # uses by queue to check result
    path_result: str = None  # uses by queue to give the result away
    error: str = None  # uses by queue to store errors with convert
    tid: str = None

    class Config:
        arbitrary_types_allowed = True

'''
Приоритеты:
Первая цифра отвечает за статус пользователя. По убыванию.
1 имеет больший приоритет, чем 4
0 - системный вызов, обрабатывается всеми ядрами сразу

Вторая цифра - приоритет файла, а так же макс. количество этих файлов для одного
процесса. В очередях (Queue.get) можно посмотреть эту  реализацию.
К примеру, если приоритет 1, то файл является самым тяжелым (sc к примеру)
и один процесс конвертирует только его.
Если приоритет = 2, то процесс берет два файла и работает с ними по очереди.
Если приоритет 3, 4, 5 и т. д., процесс также конвертирует их по очереди.
'''


class QueueManager:
    def __init__(self):
        self._queue = OrderedDict()
        self.count = 0
        self.cores = set()

    async def _init(self):
        cores = cpu_count()

        # Ядра, берущие сначала мелкие задачи. Ориентир без премиума
        if cores_count := self.get_free_cores(cores, 2):
            for _ in range(cores_count):
                self.add_core(lambda x: (self._queue[x].priory[0], -self._queue[x].priory[1]))
            cores -= cores_count

        # Ядро, берущее сначала тяжелые задачи. Ориентир без премиума
        if cores_count := self.get_free_cores(cores):
            for _ in range(cores_count):
                self.add_core(lambda x: (self._queue[x].priory[0], self._queue[x].priory[1]))
            cores -= cores_count

        # Два ядра, ориентированные на премиум. Задачи по порядку
        if cores_count := self.get_free_cores(cores, 2):
            for _ in range(cores_count):
                self.add_core(lambda x: (-self._queue[x].priory[0], self._queue[x].priory[1]))
            cores -= cores_count

        # Добор свободных ядер.
        for _ in range(cores):
            self.add_core()

    def add_core(self, sort_function=None):
        self.cores.add(self.use_core(sort_function))

    def empty(self):
        return not self._queue

    @staticmethod
    def get_free_cores(cores_count: int, priority_count: int = 1):
        if cores_count > priority_count:
            return priority_count
        return cores_count

    async def get(self, sort_function=None) -> list:
        take = []
        while self.empty():
            await asyncio.sleep(0.1)

        if sort_function:
            queue = sorted(self._queue, key=sort_function)
        else:
            queue = list(self._queue).copy()

        take.append(self._queue.popitem(last=False)[1])
        queue.pop(0)
        available = take[0].priory[1] - 1
        while available:
            for item in queue:
                if len(take) < self._queue[item].priory[1]:
                    available -= 1
                    take.append(self._queue.pop(item))
            break

        return take

    async def use_core(self, sort_function=None):
        while True:
            getter, putter = Pipe(duplex=False)
            tasks = await self.get(sort_function=sort_function)

            process = Process(target=self.start_process, args=(putter, tasks))
            process.start()
            while process.is_alive():
                await asyncio.sleep(0.1)

            result = getter.recv()
            for num, answer in enumerate(result):
                tasks[num].done = True
                if answer['converted']:
                    tasks[num].path_result = answer['path']
                else:
                    tasks[num].error = answer['error']
                    tasks[num].tid = answer['TID']

    @staticmethod
    def start_process(pipe: Pipe, objects: list[QueueFileObject]):
        result = []
        for obj in objects:
            try:
                if isinstance(obj.target, Callable):
                    answer = obj.target.__call__(*obj.arguments)

                    if isinstance(answer, Coroutine):
                        answer = asyncio.run(answer)

                    result.append(answer)
                else:
                    result.append({'converted': False, 'error': 'Target is not a function!', 'TID': None})

            except:
                result.append({'converted': False, 'error': traceback.format_exc(), 'TID': None})

        pipe.send(result)
        pipe.close()

    async def wait_for_convert(self, tasks: list[QueueFileObject]) -> list[QueueFileObject]:
        for task in tasks:
            self._queue[self.count] = task
            self.count += 1
        while not all([task.done for task in tasks]):
            await asyncio.sleep(0.1)

        return tasks
