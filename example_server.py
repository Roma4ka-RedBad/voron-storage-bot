import asyncio
import json
import os
import multiprocessing as mp
import uvicorn
import time
import heapq
import traceback
from fastapi import FastAPI
from lib import sc_to_fla, fla_to_sc

app = FastAPI()

# ну это ставит задачи в очередь
@app.get("/put_task")
async def put_task(data: dict):
    platform = data['platform']
    type = data['type']
    path = data['path']
    owner = data['owner']
    namefile = data['namefile']
    priority = data['priority']

    await q.put((priority, (type, path, owner, namefile, platform)))
    asyncio.create_task(runjob())

    return {
        'resp': True
    }


# а это берет задачи из очереди
async def runjob():
    # сначала ждет и берет любое свободное ядро
    core = await sem.get()
    # затем берет задачу
    task = await q.get()
    # информация о задаче и юзере
    type, path, owner, namefile = task[1]
    # так я отсеиваю удаленные из очереди задачи, потому что удалять из очереди
    # конкретные задачи нельзя ну или я просто ботик
    while path in ban:
        ban.remove(path)
        # это нужно, чтобы бот перестал ожидать ответа на задачу
        # ну и я наверное забыл тут создать старт, похуй
        open(path + 'del', 'w').close()
        task = await q.get()
        type, path, owner, namefile = task[1]

    if type == 'sc_to_fla':
        job = mp.Process(target=sc_to_fla_job, args=(path, namefile))

    elif type == 'fla_to_sc':
        job = mp.Process(target=fla_to_sc_job, args=(path, namefile))

    open(path + 'start', 'w').close()
    job.start()

    # это вместо job.join()
    # вроде бы join ждет завершения всех задач, а не конкретной,
    # а нужно чтобы ждал завершения конкретной задачи
    while 'e' not in os.listdir(path):
        await asyncio.sleep(0.5)

    # сигнал боту, что задача выполнена и он может отправить результат
    await asyncio.sleep(0.5)
    os.rename(path + 'e', path + 'end')
    # освобождаем ядро
    await sem.put(core)


# енкод
def sc_to_fla_job(path, file):
    try:
        start = time.time()
        sc_to_fla(path + file)
        end = time.time() - start
        response = {
            'resp': True,
            'time': end
        }

    except Exception as e:
        response = {
            'resp': 'error',
            'fullExc': str(traceback.format_exc()),
            'exc': str(e)
        }

    json.dump(response, open(path + 'e', 'w'))


# декод
def fla_to_sc_job(path, file):
    try:
        start = time.time()
        fla_to_sc(path + file)
        end = time.time() - start
        response = {
            'resp': True,
            'time': end
        }

    except Exception as e:
        response = {
            'resp': 'error',
            'fullExc': str(traceback.format_exc()),
            'exc': str(e)
        }

    json.dump(response, open(path + 'e', 'w'))


@app.get("/queue")
async def read_item():
    users = []
    que = q._queue.copy()
    for i in range(len(que)):
        entry = heapq.heappop(que)[1]
        if entry[1] not in ban:
            users.append({
                'unique_key': entry[1],
                'owner': entry[2],
                'platform': entry[4],
                'file': entry[3],
                'type': entry[0]
            })

    return users


@app.get("/del_from_queue")
async def del_from_queue(data: str):
    data = data.split(' ')
    ban.update(data)

    return {
        'response': True
    }


if __name__ == "__main__":
    # очередь с файлами
    q = asyncio.PriorityQueue()
    # очередь с ядрами, я так сделапл возможность распределения задач посвободным ядрам
    sem = asyncio.Queue()
    ban = set()
    for core in range(mp.cpu_count()):
        asyncio.run(sem.put(core))

    uvicorn.run(app, host="127.0.0.1", port=8910)
