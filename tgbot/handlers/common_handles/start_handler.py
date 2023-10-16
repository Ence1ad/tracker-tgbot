from aiogram.types import Message


async def command_start_handler(message: Message) -> Message:
    """Handle the /start command.

    :param message:
    :return:Message
    """
    return await message.answer('Start message handler')

