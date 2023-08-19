from aiogram.types import CallbackQuery

from cache.redis_cache import redis_client
from db.actions.actions_db_commands import get_user_actions
from tgbot.keyboards.callback_factories import CategoryCD
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import actions_menu_buttons

from tgbot.utils.answer_text import empty_actions_text, categories_options_text, show_action_text


async def get_actions_options(call: CallbackQuery, callback_data: CategoryCD):
    user_id = call.from_user.id
    await redis_client.hset(name=user_id, key="category_id", value=callback_data.category_id)
    markup = await menu_inline_kb(actions_menu_buttons)
    await call.message.edit_text(
        text=f"Selected category -> <i>{callback_data.category_name}</i>\n\r{categories_options_text}",
        reply_markup=markup
    )


async def display_actions(call: CallbackQuery):
    actions = list(await show_user_actions(call))
    if actions:
        await call.message.delete()
        markup = await menu_inline_kb(actions_menu_buttons)
        act_in_column = ''.join([action.action_name + '\n\r' for action in actions])
        await call.message.answer(
            text=f"{show_action_text}<i>{actions[0].category_name}</i>:\n\r{act_in_column}",
            reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_actions='🆕 Create action'))
        await call.message.edit_text(text=empty_actions_text, reply_markup=markup)


async def show_user_actions(call: CallbackQuery):
    user_id = call.from_user.id
    category_id = int(await redis_client.hget(name=user_id, key="category_id"))
    actions = await get_user_actions(user_id, category_id=category_id)
    return actions
