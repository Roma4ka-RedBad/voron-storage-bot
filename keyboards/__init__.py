from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat


async def set_commands(bot: Bot, localization, chat_id: int):
    default = []
    for command in localization.START_COMMANDS_LIST:
        default.append(BotCommand(command=command[0], description=command[1]))

    data = [
        (
            default,
            BotCommandScopeChat(chat_id=chat_id)
        )
    ]

    for commands_list, commands_scope in data:
        await bot.delete_my_commands(scope=commands_scope)
        await bot.set_my_commands(commands=commands_list, scope=commands_scope)
