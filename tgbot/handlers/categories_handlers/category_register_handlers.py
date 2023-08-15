from aiogram import F

from tgbot.utils.callback_data_classes import DeleteCategoryCallback, UpdateCategoryCallback
from tgbot.handlers.categories_handlers import new_category, get_category_name_from_user, get_categories_options, \
    display_categories, select_remove_category, del_category, select_update_category, select_category, upd_category
from tgbot.utils.states import CategoryState, UpdateCategoryState


def register_categories_handlers(router):
    # router.callback_query.register(get_categories_options, F.data == 'categories_btn')
    router.callback_query.register(display_categories, (F.data == 'categories_btn') | (F.data == 'user_categories'))
    router.callback_query.register(new_category, F.data == 'create_categories')
    router.message.register(get_category_name_from_user, CategoryState.GET_NAME)
    router.callback_query.register(select_remove_category, F.data == 'delete_categories')
    router.callback_query.register(del_category, DeleteCategoryCallback.filter())
    router.callback_query.register(select_update_category, F.data == 'update_categories')
    router.callback_query.register(select_category, UpdateCategoryCallback.filter())
    router.message.register(upd_category, UpdateCategoryState.GET_NAME)
