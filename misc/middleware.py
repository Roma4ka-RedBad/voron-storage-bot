from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class VoronStorageMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, queue_manager, convert_manager, game_manager, messengers_manager):
        super().__init__(app)
        self.queue_manager = queue_manager
        self.convert_manager = convert_manager
        self.game_manager = game_manager
        self.messengers_manager = messengers_manager

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request.state.queue_manager = self.queue_manager
        request.state.convert_manager = self.convert_manager
        request.state.game_manager = self.game_manager
        request.state.messengers_manager = self.messengers_manager
        response = await call_next(request)
        return response
