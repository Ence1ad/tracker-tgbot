import asyncio
import logging
from aiogram.filters import Command
from aiogram import Dispatcher, Router, F

# from aiogram.enums import ParseMode

# from aiogram.types import Message

from config import bot
from tgbot.handlers.categories import get_categories_options, display_categories, new_category, \
    get_category_name_from_user, select_remove_category, del_category, select_update_category, upd_category, \
    select_category
from tgbot.handlers.start import command_start_handler
from tgbot.keyboards.buttons_names import categories_btn, user_categories, create_categories, delete_categories, \
    update_categories
from tgbot.keyboards.categories_kb import DeleteCategoryCallback, UpdateCategoryCallback
from tgbot.utils.bot_commands import my_commands
from tgbot.utils.states import CategoryState, UpdateCategoryState

router = Router()


async def start_bot(tgbot):
    await my_commands(tgbot)


#
# @router.message()
# async def echo_handler(message: types.Message) -> None:
#     """
#     Handler will forward receive a message back to the sender
#
#     By default, message handler will handle all message types (like a text, photo, sticker etc.)
#     """
#     try:
#         # Send a copy of the received message
#         await message.send_copy(chat_id=message.chat.id)
#     except TypeError:
#         # But not all the types is supported to be copied so need to handle it
#         await message.answer("Nice try!")


async def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    await start_bot(bot)
    dp.include_router(router)
    router.message.register(command_start_handler, Command("start"))
    router.callback_query.register(get_categories_options, F.data == categories_btn)
    router.callback_query.register(new_category, F.data == create_categories)
    router.message.register(get_category_name_from_user, CategoryState.GET_NAME)
    router.callback_query.register(display_categories, F.data == user_categories)
    router.callback_query.register(select_remove_category, F.data == delete_categories)
    router.callback_query.register(del_category, DeleteCategoryCallback.filter())
    router.callback_query.register(select_update_category, F.data == update_categories)
    router.callback_query.register(select_category, UpdateCategoryCallback.filter())
    router.message.register(upd_category, UpdateCategoryState.GET_NAME)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(ex)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
