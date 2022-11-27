from misc import utils
from fastapi import APIRouter, Request
from database import FingerprintTable

commands_data_router = APIRouter(
    prefix="/cmddata",
    tags=["cmddata"]
)


@commands_data_router.get("/markets/{language_code}")
async def get_markets(request: Request, language_code: str):
    content = {
        1: await request.state.game_manager.get_market_data(1, language_code),
        2: await request.state.game_manager.get_market_data(2, language_code)
    }

    return await utils.create_response(True, content=content)


@commands_data_router.get("/fingerprints")
async def get_fingerprints(request: Request):
    actual_finger = FingerprintTable.get(FingerprintTable.is_actual)
    new_finger = await request.state.game_manager.server_data(actual_finger.major_v, actual_finger.build_v, actual_finger.revision_v)
    old_finger = FingerprintTable.get_or_none(FingerprintTable.id == (actual_finger.id - 1))
    content = {
        'actual_finger': actual_finger.__data__,
        'new_finger': new_finger,
        'old_finger': old_finger.__data__ if old_finger else None,
        'fingerprints': [finger.__data__ for finger in
                         FingerprintTable.select().order_by(-FingerprintTable.major_v,
                                                            -FingerprintTable.build_v).execute()],
    }

    return await utils.create_response(True, content=content)
