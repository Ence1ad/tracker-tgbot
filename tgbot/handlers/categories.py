
from telethon.events import CallbackQuery, StopPropagation

from db.categories.categories_commands import create_category, get_categories, delete_category
from tgbot.keyboards.categories_kb import categories_inline_kb, show_options_kb

from config import bot


async def list_categories_buttons(event: CallbackQuery.Event):
    await event.delete()
    markup = await categories_inline_kb()
    await bot.send_message(entity=event.chat_id,
                           message=f"Select the button",
                           buttons=markup
                           )


async def new_category(event: CallbackQuery.Event):
    await event.delete()
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message('Write new category (not > 30 characters)')
        # TODO Повесить перехват CancelTask если долго не отвечает
        response = await conv.get_response()
        if response.text.isalnum():
            await create_category(response.peer_id.user_id, response.message.strip()[:29])
            await conv.send_message(f'You successfully added new category')
        else:
            await conv.send_message(f'You can use only characters and numbers')
    raise StopPropagation


async def show_categories(event: CallbackQuery.Event):
    user_id = event.sender_id
    await event.delete()
    categories = await get_categories(user_id)
    categories = list(categories)
    if categories:
        await bot.send_message(entity=user_id, message=f"Твои категории: {', '.join(categories)}")
    else:
        await bot.send_message(entity=user_id, message=f"You don't have any categories yet")

async def remove_category(event: CallbackQuery.Event):
    user_id = event.sender_id
    await event.delete()
    # get categories from db
    categories = await get_categories(user_id)
    categories = list(categories)
    if categories:
        markup = await show_options_kb(categories)
        await bot.send_message(entity=user_id, message=f"Select the category", buttons=markup)
    else:
        await bot.send_message(entity=user_id, message=f"You don't have any categories yet")
