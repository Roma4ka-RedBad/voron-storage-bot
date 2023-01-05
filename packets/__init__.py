from .users.user import users_get, users_set
from .settings.data_by_handlers import settings_data_by_handlers
from .settings.get_config_data import settings_get_config_data
from .actions.send_message_by_count import actions_send_message_by_count
from .actions.edit_message import actions_edit_message


packets = {
    10100: settings_data_by_handlers,
    10101: settings_get_config_data,
    11100: users_get,
    11101: users_set,
    12100: actions_send_message_by_count,
    12101: actions_edit_message
}
