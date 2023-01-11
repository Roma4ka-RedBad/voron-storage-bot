from .send_message import send_message
from .edit_message import edit_message
from .delete_message import delete_message


packets = {
    22100: send_message,
    22101: edit_message,
    22102: delete_message
}
