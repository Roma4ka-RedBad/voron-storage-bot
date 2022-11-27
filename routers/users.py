from misc import utils
from fastapi import APIRouter

from logic_objects import UserObject, Metadata
from localization import languages

user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@user_router.post("/set")
async def set_user(data: UserObject):
    user = (await utils.get_user_db(data))[0]

    if '.' not in data.set_key:
        setattr(user, data.set_key, data.set_value)
        user.save()
    else:
        user_object = getattr(user, data.set_key.split('.')[0])
        setattr(user_object, data.set_key.split('.')[-1], data.set_value)
        user_object.save()

    user.__data__['metadata'] = user.metadata.__data__
    return await utils.create_response(True, content=user.__data__)


@user_router.post("/get")
async def get_user(data: UserObject):
    user = await utils.get_user_db(data)
    user[0].__data__['metadata'] = user[0].metadata.__data__
    return await utils.create_response(True, content=user[0].__data__)


@user_router.post("/connect")
async def connect_account(data: UserObject, metadata: Metadata):
    user = await utils.get_user_db(data)


@user_router.get("/localization/{language_code}")
async def get_localization(language_code: str):
    if language_code == '*':
        return await utils.create_response(True, content=languages)
    return await utils.create_response(True, content=languages[language_code])
