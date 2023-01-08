from .send_message_by_count import send_message_by_count
from .edit_message import edit_message
from .delete_message import delete_message


packets = {
    22100: send_message_by_count,
    22101: edit_message,
    22102: delete_message
}
