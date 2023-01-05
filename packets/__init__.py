from .send_message_by_count import send_message_by_count
from .edit_message import edit_message


packets = {
    12100: send_message_by_count,
    12101: edit_message
}
