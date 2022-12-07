from pydantic import BaseModel
from typing import Tuple, Any
from collections.abc import Callable


class QueueFileObject(BaseModel):
    target: Callable[[...], str] = None
    arguments: Tuple[Any] = None
    priory: Tuple[int] = (0, 3)  # system call, 0 is the highest priory
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
