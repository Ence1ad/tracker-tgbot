from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import redis_upd_tracker
from db.operations.categories_operations import update_category, select_categories, \
    select_category_id
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.states import CategoryState
from tgbot.utils.validators import valid_name


async def prompt_category_name(
        call: CallbackQuery, state: FSMContext, callback_data: CategoryCD,
        i18n: TranslatorRunner
) -> Message:
    """Prompt the user to enter a new category name.

    :param call: CallbackQuery: The callback query that triggered the prompt.
    :param state: FSMContext: The FSM (Finite State Machine) context for tracking the
    user's state.
    :param callback_data: CategoryCD: Callback data containing category information.
    :param i18n: TranslatorRunner: An instance of the translation runner for
     internationalization.
    :return: Message: A message prompting the user to enter a new category name.
    """
    category_id: int = callback_data.category_id
    category_name: str = callback_data.category_name
    await state.update_data(category_id=category_id, old_category_name=category_name)
    await state.set_state(CategoryState.WAIT_CATEGORY_DATA)
    return await call.message.edit_text(text=i18n.get('new_category_text'))


async def upd_category_name(
        message: Message, state: FSMContext, db_session: AsyncSession,
        i18n: TranslatorRunner, buttons: AppButtons, redis_client: Redis
) -> Message:
    """Update the category name based on user input.

    :param message: Message: The message containing the updated category name.
    :param state: FSMContext: The FSM (Finite State Machine) context for tracking the
     user's state.
    :param db_session: AsyncSession: An asynchronous database session.
    :param i18n: TranslatorRunner: An instance of the translation runner for
     internationalization.
    :param buttons: AppButtons: An instance of the application buttons.
    :param redis_client: Redis: An asynchronous Redis client for cache operations.
    :return: Message: A message confirming the category name update.
    """
    await message.delete()
    await state.update_data(category_name=message.text)
    user_id: int = message.from_user.id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']
    new_category_name: str = state_data['category_name']
    old_category_name: str = state_data['old_category_name']
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.categories_btn_source.category_menu_buttons(), i18n
    )
    await state.clear()
    if await select_category_id(user_id=user_id, category_name=old_category_name,
                                db_session=db_session):
        categories: Sequence = await select_categories(user_id, db_session)
        if new_category_valid_name := await valid_name(categories, new_category_name):
            await update_category(user_id, category_id, new_category_valid_name,
                                  db_session)
            await redis_set_report_need_upd(user_id=user_id, redis_client=redis_client,
                                            value=1)
            await redis_upd_tracker(user_id, redis_client,
                                    category_name=new_category_name)
            return await message.answer(
                text=i18n.get('upd_category_text', new_category_name=new_category_name),
                reply_markup=markup)
        else:
            return await message.answer(
                text=i18n.get('category_exists_text', new_line='\n',
                              new_category_name=new_category_name), reply_markup=markup
            )
    else:
        return await message.answer(text=i18n.get('valid_data_text'),
                                    reply_markup=markup)
