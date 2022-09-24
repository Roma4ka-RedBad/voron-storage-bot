import uvicorn
import asyncio
import os

from fastapi import FastAPI
from typing import List

from models import *
from utils import *

UFS_path = '../ufs/'
server = FastAPI()


@server.post("/get_buttons")
async def get_buttons(files: List[FileObject], client: ClientObject):
    content = {}
    for file in files:
        if os.path.exists(UFS_path + f'{client.messenger}/{file.name}'):
            if file.size_to_gb() < 1:
                tasks = await get_task_for_format(file.format, UFS_path + f'{client.messenger}/{file.name}')
                content.update({file.name: tasks})
            else:
                return await create_response(False, error_msg='Файл слишком много весит!')
        else:
            return await create_response(False, error_msg='Файл не найден!')

    return await create_response(True, content=content)

uvicorn.run(server, host="192.168.0.127", port=8910)
