from vkbottle import Keyboard


def compressed_photos_keyboard(message_id: int) -> str:
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .schema(
            [
                [
                    {
                        'label': 'PNG',
                        'type': 'callback',
                        'color': 'positive',
                        'payload': {
                            'msg_id': message_id,
                            'type': 'convert',
                            'convert_to': 'png'
                        }
                    },
                    {
                        'label': 'JPG',
                        'type': 'callback',
                        'color': 'positive',
                        'payload': {
                            'msg_id': message_id,
                            'type': 'convert',
                            'convert_to': 'jpg'
                        }
                    }
                ],
                [
                    {
                        'label': 'KTX',
                        'type': 'callback',
                        'color': 'negative',
                        'payload': {
                            'TID': 'TID_SNACKBAR_METHOD_IS_UNAVAILABLE',
                            'type': 'show_snackbar'
                        }
                    },
                    {
                        'label': 'PVR',
                        'type': 'callback',
                        'color': 'negative',
                        'payload': {
                            'TID': 'TID_SNACKBAR_METHOD_IS_UNAVAILABLE',
                            'type': 'show_snackbar'
                        }
                    },
                    {
                        'label': 'SC',
                        'type': 'callback',
                        'color': 'negative',
                        'payload': {
                            'TID': 'TID_SNACKBAR_METHOD_IS_UNAVAILABLE',
                            'type': 'show_snackbar'
                        }
                    }
                ]
            ]
        )
        .get_json()
    )

    return keyboard
