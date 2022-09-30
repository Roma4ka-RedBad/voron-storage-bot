import uvicorn

from fastapi import FastAPI
from typing import List

from models import files_object, config
import utils

config = config.Config('config.ini')
server = FastAPI()


@server.get("/config")
async def get_config():
    return await utils.create_response(True, content=config.box)


@server.get("/limit/{file_format}")
async def get_limit(file_format: str):
    return await utils.create_response(True, content=config.get_size_by_format(file_format) * 1024 * 1024)


@server.post("/converts")
async def get_converts(files: List[files_object.FileObject]):
    if len(files) > 1:
        content = []
        for file in files:
            file.set_config(config)
            converts = []
            if file.is_exist():
                converts = await utils.get_converts_for_format(file)

            content.append({
                'name': file.name,
                'converts': converts
            })
        return await utils.create_response(True, content=content)

    else:
        files[0].set_config(config)
        converts = await utils.get_converts_for_format(files[0])
        if converts:
            return await utils.create_response(True, content={
                'name': files[0].name,
                'converts': converts
            })

        return await utils.create_response(False,
                                           error_msg="Этот файл нельзя конвертировать ни в один из доступных форматов!")


uvicorn.run(server, host="192.168.0.127", port=8910)
