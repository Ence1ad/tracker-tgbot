from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import redis_delete_tracker
from db.operations.actions_operations import delete_action
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import ActionCD
from tgbot.keyboards.inline_kb import menu_inline_kb


async def delete_action_handler(
        call: CallbackQuery, callback_data: ActionCD, db_session: AsyncSession,
        redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Handle the deletion of an existing action.

    This handler is triggered when a user attempts to delete an existing action.
    It handles the action deletion process, including updating the database and
    informing the user of the result.

    :param call: CallbackQuery: The user's callback query.
    :param callback_data: ActionCD: The callback data containing action information.
    :param db_session: AsyncSession: The database session for database operations.
    :param redis_client: Redis: The Redis client for caching operations.
    :param buttons: AppButtons: The app's button source.
    :param i18n: TranslatorRunner: The translator runner for handling
    internationalization.
    :return: Message: The response message to be sent to the user.
    """
    user_id: int = call.from_user.id
    action_id: int = callback_data.action_id
    action_name: str = callback_data.action_name
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.actions_btn_source.action_menu_buttons(), i18n)
    await redis_delete_tracker(user_id, redis_client)
    await redis_set_report_need_upd(user_id=user_id, redis_client=redis_client, value=1)
    db_returning: int = await delete_action(user_id, action_id, db_session)
    if db_returning:
        return await call.message.edit_text(
            text=i18n.get('rm_action_text', action_name=action_name),
            reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('action_not_exists_text'),
                                            reply_markup=markup)
