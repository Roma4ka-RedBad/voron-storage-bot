import uvicorn
import asyncio

from fastapi import FastAPI
from typing import List

from models import file, config
import utils

config = config.Config('config.ini')
server = FastAPI()


@server.get("/limit/{file_format}")
async def get_limit(file_format):
    return await utils.create_response(True, content=config.get_size_by_format(file_format))


@server.post("/buttons")
async def get_buttons(files: List[file.FileObject]):
    content = {}
    for file in files:
        tasks = []
        file.set_config(config)

        if file.is_exist():
            tasks = await utils.get_task_for_format(file)

        content.update({file.name: tasks})

    return await utils.create_response(True, content=content)


uvicorn.run(server, host="192.168.0.127", port=8910)
