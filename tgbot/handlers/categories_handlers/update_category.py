from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import redis_upd_tracker
from db.operations.categories_operations import update_category, select_categories, select_category_id
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.states import CategoryState
from tgbot.utils.validators import valid_name


async def prompt_category_name(call: CallbackQuery, state: FSMContext, callback_data: CategoryCD, i18n: TranslatorRunner
                               ) -> Message:
    """
    The prompt_category_name function updates the state with data about which category was clicked and what its name is,
     then sets the state to WAIT_CATEGORY_DATA and edits the message text to prompt for a new name.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param state: FSMContext: Store the state of the conversation
    :param callback_data: CategoryCD: Get the category_id and category_name from the callback data
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the text
    """
    category_id: int = callback_data.category_id
    category_name: str = callback_data.category_name
    await state.update_data(category_id=category_id, old_category_name=category_name)
    await state.set_state(CategoryState.WAIT_CATEGORY_DATA)
    return await call.message.edit_text(text=i18n.get('new_category_text'))


async def upd_category_name(message: Message, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                            i18n: TranslatorRunner, buttons: AppButtons, redis_client: Redis) -> Message | FSMContext:
    """
    The upd_category_name function is used to update the name of a category.

    :param message: Message: Get the message object that was sent by the user
    :param state: FSMContext: Store the data in the state machine
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :param buttons: AppButtons: Get the buttons from the middleware
    :param redis_client: Redis: Get the redis client from the middleware
    :return: The message text and the inline keyboard with categories menu buttons
    """
    await message.delete()
    await state.update_data(category_name=message.text)
    user_id: int = message.from_user.id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']
    new_category_name: str = state_data['category_name']
    old_category_name: str = state_data['old_category_name']
    # Is the text checking
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.categories_btn_source.category_menu_buttons(),
                                                        i18n)
    await state.clear()
    if await select_category_id(user_id=user_id, category_name=old_category_name, db_session=db_session):
        categories: list[Row] = await select_categories(user_id, db_session)  # If message a text
        if new_category_valid_name := await valid_name(categories, new_category_name):
            await update_category(user_id, category_id, new_category_valid_name, db_session)
            await redis_set_report_need_upd(user_id=user_id, redis_client=redis_client, value=1)
            await redis_upd_tracker(user_id, redis_client, category_name=new_category_name)
            return await message.answer(text=i18n.get('upd_category_text', new_category_name=new_category_name),
                                        reply_markup=markup)
        else:
            return await message.answer(text=i18n.get('category_exists_text', new_line='\n',
                                                      new_category_name=new_category_name), reply_markup=markup)
    else:
        return await message.answer(text=i18n.get('valid_data_text'), reply_markup=markup)
