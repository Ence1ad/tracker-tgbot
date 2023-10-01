from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import is_redis_hexists_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import started_tracker_text


async def command_start_handler(message: Message, db_session: async_sessionmaker[AsyncSession], redis_client: Redis,
                                buttons: AppButtons, i18n: TranslatorRunner, state: FSMContext) -> Message:
    """
    Handle the /start command.

    :param message: Message: Get the message object that was sent by the user
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param redis_client: Redis: Get the redis client from the middleware. Check and add user id to the redis set
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
    :param state: FSMCobtext: : Store the state of the user in a conversation
     Translate the buttons and the message text
    :return: The message text and the inline keyboard with start menu buttons

    """
    user_id: int = message.from_user.id
    await message.delete()
    await state.clear()
    markup: InlineKeyboardMarkup = await start_menu_inline_kb(await buttons.main_menu_buttons(), i18n)
    if await is_redis_hexists_tracker(user_id, redis_client):
        started_text: str = await started_tracker_text(user_id=user_id, redis_client=redis_client, i18n=i18n,
                                                  title='started_tracker_title')
        return await message.answer(text=started_text, reply_markup=markup)
    else:
        return await message.answer(text=i18n.get('user_in_db_text'), reply_markup=markup)