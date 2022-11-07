from vkbottle import Keyboard, Callback, KeyboardButtonColor
from typing import List, Tuple


class Colors:
    positive = KeyboardButtonColor.POSITIVE
    negative = KeyboardButtonColor.NEGATIVE
    primary = KeyboardButtonColor.PRIMARY
    secondary = KeyboardButtonColor.SECONDARY


def converts_keyboard(buttons: List[List[str] | Tuple[str] | str],
                      localization,
                      message_id: int,
                      one_time: bool = False,
                      inline: bool = True,
                      page: int = 1,
                      **payload) -> str | None:
    need_last_row = False
    max_buttons = 10 if inline else 40
    one_time = False if inline else one_time
    keyboard = Keyboard(one_time=one_time, inline=inline)
    data = []

    for obj in buttons:
        if isinstance(obj, (List, Tuple)):
            for item in obj:
                if item not in data:
                    data.append(item)
        else:
            data.append(obj)
    is_last_page = len(data) <= page * (max_buttons - 2)

    if len(data) > max_buttons:
        data = data[(page - 1) * (max_buttons - 2):page * (max_buttons - 2)]
        need_last_row = True

    if not data:
        return None

    max_buttons_in_row = 3 if len(data) % 2 else 2
    buttons_in_row = 0
    for arg in data:
        if buttons_in_row == max_buttons_in_row:
            keyboard.row()
            buttons_in_row = 0
        keyboard.add(Callback(arg, payload={'msg_id': message_id,
                                            'type': 'doc_convert',
                                            'convert_to': arg, **payload}),
                     color=Colors.primary)
        buttons_in_row += 1

    if page > 1 or need_last_row:
        keyboard.row()
        if page == 1:
            keyboard.add(
                Callback(localization.TID_SWITCH_LEFT,
                         payload={'TID': 'TID_IS_START_PAGE',
                                  'type': 'show_snackbar'}),
                color=Colors.negative)
            keyboard.add(Callback(localization.TID_SWITCH_RIGHT,
                                  payload={'msg_id': message_id,
                                           'type': 'move_page',
                                           'page': page + 1,
                                           **payload}),
                         color=Colors.positive)

        elif is_last_page:
            keyboard.add(Callback(localization.TID_SWITCH_LEFT,
                                  payload={'msg_id': message_id,
                                           'type': 'move_page',
                                           'page': page - 1,
                                           **payload}),
                         color=Colors.positive)
            keyboard.add(Callback(localization.TID_SWITCH_RIGHT,
                                  payload={'TID': 'TID_IS_LAST_PAGE',
                                           'type': 'show_snackbar'}),
                         color=Colors.negative)
        else:
            keyboard.add(Callback(localization.TID_SWITCH_LEFT,
                                  payload={'msg_id': message_id,
                                           'type': 'move_page',
                                           'page': page - 1,
                                           **payload}),
                         color=Colors.positive)
            keyboard.add(Callback(localization.TID_SWITCH_RIGHT,
                                  payload={'msg_id': message_id,
                                           'type': 'move_page',
                                           'page': page + 1,
                                           **payload}),
                         color=Colors.positive)

    return keyboard.get_json()
