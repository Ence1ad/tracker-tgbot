from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner


async def command_cancel_handler(message: Message, state: FSMContext, i18n: TranslatorRunner) -> Message:

    """
    The command_cancel_handler function is a handler for the /cancel command.
    It clears the state and deletes the message that triggered it, then sends the cancellation message.

    :param message: Message: Object represents the telegram message
    :param state: FSMContext: Store the state of a conversation
    :param i18n: TranslatorRunner: Get the language of the user
    :return: The cancellation message

    """
    await state.clear()
    await message.delete()
    return await message.answer(text=i18n.get('canceling_text'))


async def callback_cancel_handler(call: CallbackQuery, state: FSMContext, i18n: TranslatorRunner) -> bool:
    """
    The callback_cancel_handler function is a callback handler
    that clears the state and sends an exit message to the user.
    It also deletes the message that triggered it.

    :param call: CallbackQuery: Get the message object that was sent by the user
    :param state: FSMContext: Store the state of the bot
    :param i18n: TranslatorRunner: Get the language of the user from the middleware
    :return: A boolean value

    """
    await state.clear()
    is_answer: bool = await call.answer(text=i18n.get('exit_text'))
    await call.message.delete()
    return is_answer
