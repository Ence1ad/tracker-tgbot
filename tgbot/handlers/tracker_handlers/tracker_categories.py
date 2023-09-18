from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import is_redis_hexists_tracker, redis_get_user_day_trackers
from config import settings
from db.categories.categories_commands import select_categories
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import select_category_text, already_launch_tracker_text, \
    empty_categories_text, started_tracker_text, tracker_daily_limit_text
from tgbot.keyboards.callback_factories import CategoryOperation


async def select_category_tracker(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                                  redis_client: Redis, buttons: AppButtons) -> Message:
    user_id = call.from_user.id
    await call.message.delete()
    is_tracker = await is_redis_hexists_tracker(user_id, redis_client)
    # TODO разбить на несколько функций
    if not is_tracker:
        user_trackers_cnt = await redis_get_user_day_trackers(user_id, redis_client)
        if user_trackers_cnt is None or (int(user_trackers_cnt) < settings.USER_TRACKERS_DAILY_LIMIT):
            categories = await select_categories(user_id, db_session)
            if categories:
                markup = await callback_factories_kb(categories, CategoryOperation.READ_TRACKER)
                return await call.message.answer(text=select_category_text, reply_markup=markup)
            else:
                markup = await menu_inline_kb(await buttons.new_category())
                return await call.message.answer(text=empty_categories_text, reply_markup=markup)
        else:
            markup = await menu_inline_kb(await buttons.tracker_menu_start())
            return await call.message.answer(text=tracker_daily_limit_text, reply_markup=markup)
    else:
        started_tracker = await started_tracker_text(user_id, redis_client)
        markup = await menu_inline_kb(await buttons.yes_no_menu())
        return await call.message.answer(text=already_launch_tracker_text + started_tracker, reply_markup=markup)
