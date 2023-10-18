from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import redis_delete_tracker
from db.operations.categories_operations import delete_category
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD
from tgbot.keyboards.inline_kb import menu_inline_kb


async def delete_category_handler(
        call: CallbackQuery, callback_data: CategoryCD, db_session: AsyncSession,
        redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner,
        state: FSMContext
) -> Message:
    """Handle the deletion of a user's category.

    :param call: CallbackQuery: The callback query that triggered the category deletion.
    :param callback_data: CategoryCD: The callback data that contains information about
     the category.
    :param db_session: AsyncSession: An asynchronous database session.
    :param redis_client: Redis: An asynchronous Redis client.
    :param buttons: AppButtons: An instance of the application buttons.
    :param i18n: TranslatorRunner: An instance of the translation runner for
    internationalization.
    :param state: FSMContext: The FSM (Finite State Machine) context for tracking the
    user's state.
    :return: Message: A message to inform the user about the status of the category
     deletion.
    """
    user_id: int = call.from_user.id
    category_id: int = callback_data.category_id
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.categories_btn_source.category_menu_buttons(), i18n
    )
    await redis_delete_tracker(user_id, redis_client)
    await redis_set_report_need_upd(user_id=user_id, redis_client=redis_client, value=1)
    returning: int = await delete_category(user_id, category_id, db_session)
    if returning:
        await state.clear()
        return await call.message.edit_text(text=i18n.get('rm_category_text'),
                                            reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('categories_is_fake_text'),
                                            reply_markup=markup)
