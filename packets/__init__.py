from .send_message import send_message
from .edit_message import edit_message
from .delete_message import delete_message


packets = {
    20100: send_message,
    20101: edit_message,
    20102: delete_message
}
