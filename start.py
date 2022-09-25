import uvicorn
import asyncio

from fastapi import FastAPI
from typing import List

from models import file
import utils

server = FastAPI()


@server.post("/get_buttons")
async def get_buttons(files: List[file.FileObject]):
    content = {}
    for file in files:
        if file.is_exist():
            if file.size_to_gb() < 1:
                tasks = await utils.get_task_for_format(file)
                content.update({file.name: tasks})
            else:
                return await utils.create_response(False, error_msg='Файл слишком много весит!')
        else:
            return await utils.create_response(False, error_msg='Файл не найден!')

    return await utils.create_response(True, content=content)


uvicorn.run(server, host="192.168.0.127", port=8910)
