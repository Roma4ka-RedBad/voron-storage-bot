from box import Box
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


def audio_keyboard(message_id: int, localization) -> str:
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .schema(
            [
                [
                    {
                        'label': localization.TID_CONVERT_TO.format(format='mp3'),
                        'type': 'callback',
                        'color': 'positive',
                        'payload': {
                            'msg_id': message_id,
                            'type': 'audio_convert',
                            'convert_to': 'mp3',
                            'compress': False
                            }
                        },
                    {
                        'label': localization.TID_CONVERT_TO.format(format='ogg'),
                        'type': 'callback',
                        'color': 'positive',
                        'payload': {
                            'msg_id': message_id,
                            'type': 'audio_convert',
                            'convert_to': 'ogg',
                            'compress': False
                            }
                        }
                    ],
                [
                    {
                        'label': localization.TID_CONVERT_AND_COMPRESS.format(format='mp3'),
                        'type': 'callback',
                        'color': 'secondary',
                        'payload': {
                            'msg_id': message_id,
                            'type': 'audio_convert',
                            'convert_to': 'mp3',
                            'compress': True
                            }
                        },
                    {
                        'label': localization.TID_CONVERT_AND_COMPRESS.format(format='ogg'),
                        'type': 'callback',
                        'color': 'secondary',
                        'payload': {
                            'msg_id': message_id,
                            'type': 'audio_convert',
                            'convert_to': 'ogg',
                            'compress': True
                            }
                        }

                    ]
                ]
            )
        .get_json()
        )

    return keyboard


def commands_keyboard(localization) -> str:
    tids = Box(localization.VK_COMMANDS_KEYBOARD)
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .schema(
            [
                [
                    {'label': tids.game_versions, 'type': 'text', 'color': 'primary'},
                    {'label': tids.about_game, 'type': 'text', 'color': 'primary'},
                    {'label': tids.download_file, 'type': 'text', 'color': 'primary'}
                    ],
                [{'label': tids.profile, 'type': 'text', 'color': 'positive'}],
                [
                    {'label': tids.change_nickname, 'type': 'text', 'color': 'secondary'},
                    {'label': tids.bind_account, 'type': 'text', 'color': 'secondary'}
                    ],

                ]
            )
        .get_json()
        )

    return keyboard


def change_language_keyboard(localization):
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .schema([
            [{
                'label': localization.TID_SET_LANGUAGE,
                'type': 'callback',
                'payload': {'command': 'change_language'}}]
            ])
        .get_json()
        )

    return keyboard
