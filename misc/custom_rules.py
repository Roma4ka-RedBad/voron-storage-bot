from vkbottle.dispatch.rules import ABCRule
from vkbottle.tools.dev.mini_types.base import BaseMessageMin
import re


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


class StartFromRule(ABCRule):
    def __init__(self, *patterns: str, regex_pattern = None, ignore_case: bool = True, args_must_be: bool = True):
        self.regex_pattern = regex_pattern
        self.patterns = list(patterns)
        self.ignore_case = ignore_case
        self.args_must_be = args_must_be

    async def check(self, message):
        if self.regex_pattern:
            if self.ignore_case:
                match = re.match(self.regex_pattern, message.text, re.IGNORECASE)
            else:
                match = re.match(self.regex_pattern, message.text)

            if match:
                message.text = message.text[match.end():]
                return {'message': message}

        for pattern in self.patterns:
            if self.ignore_case:
                if message.text.lower().startswith(pattern.lower()):
                    message.text = message.text[len(pattern):].strip()
                    if self.args_must_be and len(message.text) > 0:
                        return {'message': message}
                    else:
                        return {'message': message}
            else:
                if message.text.startswith(pattern.lower()):
                    message.text = message.text[len(pattern):].strip()
                    if self.args_must_be and len(message.text) > 0:
                        return {'message': message}
                    else:
                        return {'message': message}

        return False
