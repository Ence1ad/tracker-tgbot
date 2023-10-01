from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_delete_tracker
from db.actions.actions_db_commands import delete_action
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import ActionCD
from tgbot.keyboards.inline_kb import menu_inline_kb


async def delete_action_handler(
        call: CallbackQuery, callback_data: ActionCD, db_session: async_sessionmaker[AsyncSession],
        redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """
    The delete_action_handler function is used to delete an action from the database.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param callback_data: ActionCD: Get the action_id and action_name from the callback data
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param redis_client: Redis: Get the redis client from the middleware. Delete the tracker from redis db
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the text and the start action menu buttons
    """
    user_id: int = call.from_user.id
    action_id: int = callback_data.action_id
    action_name: str = callback_data.action_name
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.actions_btn_source.action_menu_buttons(), i18n)
    await redis_delete_tracker(user_id, redis_client)
    db_returning: int = await delete_action(user_id, action_id, db_session)
    if db_returning:
        return await call.message.edit_text(text=i18n.get('rm_action_text', action_name=action_name),
                                            reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('action_not_exists_text'), reply_markup=markup)
