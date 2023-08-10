import asyncio
import logging

from telethon.events import NewMessage, CallbackQuery

from config import bot
from tgbot.handlers.start import start
from tgbot.handlers.categories import list_categories_buttons, new_category, show_categories,\
    remove_category


async def main():
    bot.add_event_handler(start, NewMessage(incoming=True, pattern='/start'))
    bot.add_event_handler(list_categories_buttons, CallbackQuery(data=b'categories_btn'))
    bot.add_event_handler(new_category, CallbackQuery(data=b'create_categories'))
    bot.add_event_handler(show_categories, CallbackQuery(data=b'my_categories'))
    bot.add_event_handler(remove_category, CallbackQuery(data=b'delete_categories'))
    # bot.add_event_handler(get_category_name, CallbackQuery())
    await bot.run_until_disconnected()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
