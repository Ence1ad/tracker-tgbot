from aiogram import F, Router

from tgbot.keyboards.app_buttons import AppButtons


def register_categories_handlers() -> Router:
    from .delete_category import get_del_categories, del_category
    from .create_category import prompt_new_category_handler, create_category_handler
    from .show_categories import display_categories
    from .update_category import get_upd_categories, upd_category_name, prompt_category_name

    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation
    from tgbot.utils.states import CategoryState

    router = Router()

    router.callback_query.register(display_categories, (F.data == AppButtons.general_data.CATEGORIES_BTN.name)
                                   | (F.data == AppButtons.categories_data.USER_CATEGORIES.name))
    router.callback_query.register(prompt_new_category_handler,
                                   F.data == AppButtons.categories_data.CREATE_CATEGORIES.name)
    router.message.register(create_category_handler, CategoryState.GET_NAME)
    router.callback_query.register(get_upd_categories,
                                   F.data == AppButtons.categories_data.UPDATE_CATEGORIES.name)
    router.callback_query.register(prompt_category_name, CategoryCD.filter(F.operation == CategoryOperation.UPD))
    router.message.register(upd_category_name, CategoryState.WAIT_CATEGORY_DATA)
    # router.message.register(upd_category_handler, CategoryState.UPD_CATEGORY_NAME)
    router.callback_query.register(get_del_categories,
                                   F.data == AppButtons.categories_data.DELETE_CATEGORIES.name)
    router.callback_query.register(del_category, CategoryCD.filter(F.operation == CategoryOperation.DEL))

    return router
