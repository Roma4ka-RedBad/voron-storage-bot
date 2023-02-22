from .users.user import users_get, users_set
from .client.data_by_handlers import client_data_by_handlers
from .client.get_config_data import client_get_config_data
from .client.bot_ids_by_object import client_bot_ids_by_object
from .actions.send_error import action_send_error
from .brawlstars.get_fingers import brawlstars_get_fingers
from .brawlstars.get_markets_data import brawlstars_get_markets_data
from .brawlstars.search_files_by_query import brawlstars_search_files_query
from .brawlstars.normal_searching_files import normal_brawlstars_search_files_query
from .brawlstars.download_files_by_query import brawlstars_download_files_query
from .brawlstars.convert import convert
from .files.register import files_register
from .files.check_file import files_check


packets = {
    10100: client_data_by_handlers,
    10101: client_get_config_data,
    10102: client_bot_ids_by_object,
    11100: users_get,
    11101: users_set,
    12100: action_send_error,
    13100: brawlstars_get_fingers,
    13101: brawlstars_get_markets_data,
    13102: brawlstars_search_files_query,
    13202: normal_brawlstars_search_files_query,
    13103: brawlstars_download_files_query,
    13104: convert,
    14100: files_register,
    14101: files_check
}
