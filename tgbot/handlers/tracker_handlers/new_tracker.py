from aiogram.types import CallbackQuery

from cache.redis_cache import redis_client
from tgbot.utils.answer_text import new_tracker_text
from tgbot.keyboards.callback_factories import ActionCD

from db.tracker.tracker_db_command import create_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_stop


# TODO трекер должен автоматом останавливаться через нужное время
async def create_new_tracker(call: CallbackQuery, callback_data: ActionCD):
    user_id = call.from_user.id
    start_time = call.message.date
    action_name = callback_data.action_name
    action_id = callback_data.action_id
    category_name = (await redis_client.hget(name=user_id, key='category_name')).decode(encoding='utf-8')
    await redis_client.hmset(name=f"{user_id}_tracker",
                             mapping={"start_time": str(call.message.date),
                                      "action_name": callback_data.action_name,
                                      "category_name": category_name
                                      })
    await create_tracker(user_id, category_name=category_name, action_id=action_id,
                         track_start=start_time)
    markup = await menu_inline_kb(tracker_menu_buttons_stop)
    await call.message.edit_text(text=f"{new_tracker_text} {action_name}", reply_markup=markup)
