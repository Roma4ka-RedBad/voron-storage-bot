from keyboards import commands_keyboard
from vkbottle.bot import Message

from bot_config import Config
from misc.handler_utils import commands_to_regex

labeler = Config.labelers.new()
labeler.vbml_ignore_case = True


@labeler.private_message(regexp=commands_to_regex('команды', 'помощь', 'commands', 'help'))
@labeler.private_message(text=('команды', 'помощь', 'commands', 'help'))
async def commands_handler(message: Message, localization):
    keyboard = commands_keyboard(localization)
    await message.answer(localization.START_VK_COMMANDS, keyboard=keyboard)


@labeler.private_message(text=('Начать', 'start'))
async def hello_handler(message: Message, localization, userdata):
    user = await message.get_user()
    keyboard = commands_keyboard(localization)
    nickname = userdata.nickname or f'{user.first_name}'
    await message.answer(localization.START_VK_BODY.format(name=nickname), keyboard=keyboard)
