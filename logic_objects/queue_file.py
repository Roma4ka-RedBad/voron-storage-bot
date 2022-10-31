from pydantic import BaseModel
from typing import Tuple, Any
from collections.abc import Callable, Coroutine, Awaitable


class QueueFileObject(BaseModel):
    target: Callable[[...], str] | Awaitable | Coroutine = None
    arguments: Tuple[Any] = None
    priory: Tuple[int] = (0, 10)  # system call, 0 is the highest priory
    done: bool = False  # uses by queue to check result
    path_result: str = None  # uses by queue to give the result away

    class Config:
        arbitrary_types_allowed = True

'''
Приоритеты:
Первая цифра отвечает за статос пользователя.
0 - системный вызов, обрабатывается всеми ядрами сразу
1 - премиум пользователь
2 - обычный пользователь

Вторая цифра - приоритет файла, а так же макс. количество этих файлов для одного
процесса. В очередях (Queue.get) можно посмотреть эту  реализацию.
К примеру, если приоритет 1, то файл является самым тяжелым (sc к примеру)
и один процесс конвертирует только его.
Если приоритет = 2, то процесс берет два файла и работает с ними по очереди.
Если приоритет 3, 4, 5 и т. д., процесс также конвертит их по очереди.
'''
