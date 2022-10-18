from vkbottle.dispatch.rules import ABCRule
from vkbottle.tools.dev.mini_types.base import BaseMessageMin


class PayloadRule(ABCRule):
    def __init__(self, payload: dict | list[dict, ...]):
        if isinstance(payload, dict):
            self.patterns = [list(payload.items())]
        else:
            self.patterns = [list(i.items()) for i in payload]

    async def check(self, event: BaseMessageMin) -> bool:
        if event.type == 'message_event':
            payload = list(event.object.payload.items())
        else:
            payload = list(event.get_payload_json().items()) or list(event.payload.items())

        temp = []
        for pattern in self.patterns:
            temp.append(all(i in payload for i in pattern))

        return any(temp)
