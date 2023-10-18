from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner


async def command_cancel_handler(message: Message, state: FSMContext,
                                 i18n: TranslatorRunner) -> Message:
    """Handle the user's request to cancel the current operation or action.

    :param message: Message: The Message object representing the user's request.
    :param state: FSMContext: The finite state machine (FSM) context for the user.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :return: Message: A response message indicating the cancellation of the operation.
    """
    await state.clear()
    await message.delete()
    return await message.answer(text=i18n.get('canceling_text'))


async def callback_cancel_handler(call: CallbackQuery, state: FSMContext,
                                  i18n: TranslatorRunner) -> bool:
    """Handle a user's callback query to cancel the current operation or action.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    callback.
    :param state: FSMContext: The finite state machine (FSM) context for the user.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :return:  bool: A boolean value indicating if the cancellation request was
     acknowledged.
    """
    await state.clear()
    is_answer: bool = await call.answer(text=i18n.get('exit_text'))
    await call.message.delete()
    return is_answer
