from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import redis_delete_tracker
from db.categories.categories_commands import delete_category
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD
from tgbot.keyboards.inline_kb import menu_inline_kb


async def delete_category_handler(
        call: CallbackQuery, callback_data: CategoryCD, db_session: async_sessionmaker[AsyncSession],
        redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner, state: FSMContext
) -> Message:
    """
    The delete_category_handler function is responsible for deleting a category from the database.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param callback_data: CategoryCD: Get the category_id from the callback data
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param redis_client: Redis: Connect to the redis database
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :param state: FSMContext: Clear the state of the user after deleting a category
    :return: A message
    """
    user_id: int = call.from_user.id
    category_id: int = callback_data.category_id
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.categories_btn_source.category_menu_buttons(),
                                                        i18n)
    await redis_delete_tracker(user_id, redis_client)
    await redis_set_report_need_upd(user_id=user_id, redis_client=redis_client, value=1)
    returning: int = await delete_category(user_id, category_id, db_session)
    if returning:
        await state.clear()
        return await call.message.edit_text(text=f"{i18n.get('rm_category_text')}", reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('categories_is_fake_text'), reply_markup=markup)
