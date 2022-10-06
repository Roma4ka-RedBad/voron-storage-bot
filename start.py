import uvicorn
import utils

from fastapi import FastAPI
from typing import List

from models import files_object, config, database
from localization import languages
from database import User

config = config.Config('config.ini')
server = FastAPI()


@server.get("/localization/{language_code}")
async def get_localization(language_code: str):
    return await utils.create_response(True, content=languages[language_code])


@server.post("/user/set")
async def set_user(data: database.UserModel):
    user = User.get(vk_id=data.vk_id, tg_id=data.tg_id)
    setattr(user, data.set_key, data.set_value)
    user.save()
    return await utils.create_response(True, content=user)


@server.post("/user/get")
async def get_user(data: database.UserModel):
    return await utils.create_response(True, content=User.get_or_create(vk_id=data.vk_id, tg_id=data.tg_id)[0])


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
        if converts and not files[0].is_archive():
            return await utils.create_response(True, content={
                'name': files[0].name,
                'converts': converts
            })
        else:
            if converts['files'] or converts['converts']:
                return await utils.create_response(True, content={
                    'name': files[0].name,
                    'converts': converts
                })

        return await utils.create_response(False,
                                           error_msg="TID_WORK_FORMATSNOTEXIST")


uvicorn.run(server, host="192.168.0.127", port=8910)
