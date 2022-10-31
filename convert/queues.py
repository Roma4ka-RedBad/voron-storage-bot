from multiprocessing import Process, Pipe, cpu_count
from collections import OrderedDict
from collections.abc import Callable, Coroutine
import asyncio

from logic_objects.queue_file import QueueFileObject


class QueueManager:
    def __init__(self, auto_set_cores=True):
        self._queue = OrderedDict()
        self.count = 0
        if auto_set_cores:
            asyncio.run(self._init())

    async def _init(self):
        # Ядра, берущие сначала мелкие задачи. Ориентир без премиума
        for _ in range(2):
            asyncio.create_task(
                self.use_core(
                    lambda x: (self._queue[x].priory[0], -self._queue[x].priory[1])))

        # Ядро, берущее сначала тяжелые задачи. Ориентир без премиума
        asyncio.create_task(
            self.use_core(
                lambda x: (self._queue[x].priory[0], self._queue[x].priory[1])))

        # Два ядра, ориентированные на премиум. Задачи по порядку
        for _ in range(2):
            asyncio.create_task(
                self.use_core(
                    lambda x: (-self._queue[x].priory[0], self._queue[x].priory[1])))

        # Добор свободных ядер. На моем сервере их 6
        # ядра, которые просто берут задачи по-порядку
        for _ in range(cpu_count() - 5):
            asyncio.create_task(self.use_core())

    def empty(self):
        return not self._queue

    async def get(self, sort_function=None) -> list:
        take = []
        while self.empty():
            await asyncio.sleep(0)

        if sort_function:
            queue = sorted(self._queue, key=sort_function)
        else:
            queue = list(self._queue).copy()

        take.append(self._queue.popitem(last=False)[1])
        queue.pop(0)
        available = take[0].priory[1] - 1
        while available:
            for item in queue:
                if self._queue[item].priory[1] < len(take):
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
                await asyncio.sleep(0.01)

            result = getter.recv()
            for num, answer in enumerate(result):
                tasks[num].path_result = answer
                tasks[num].done = True

    @staticmethod
    def start_process(pipe: Pipe, objects: list[QueueFileObject]):
        result = []
        for obj in objects:
            print(obj)
            if isinstance(obj.target, Coroutine):
                result.append(asyncio.run(obj.target))

            elif isinstance(obj.target, Callable):
                result.append(obj.target.__call__(*obj.arguments))

            else:
                result.append('Target is not a function!')

        pipe.send(result)
        pipe.close()

    async def wait_for_convert(self, tasks: list[QueueFileObject]) -> list[QueueFileObject]:
        for task in tasks:
            self._queue[self.count] = task
            self.count += 1
        while not all([task.done for task in tasks]):
            await asyncio.sleep(0)

        return tasks
