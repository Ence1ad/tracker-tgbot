from aiogram import F, Router

from tgbot.keyboards.app_buttons import AppButtons


def register_categories_handlers() -> Router:
    from .delete_category import pick_removing_category_handler, del_category
    from .create_category import prompt_new_category_handler, create_category_handler
    from .show_categories import display_categories
    from .update_category import select_update_category, upd_category, select_category

    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation
    from tgbot.utils.states import CategoryState, UpdateCategoryState

    router = Router()

    router.callback_query.register(display_categories, (F.data == AppButtons.general_data.CATEGORIES_BTN.name)
                                   | (F.data == AppButtons.categories_data.USER_CATEGORIES.name))
    router.callback_query.register(prompt_new_category_handler,
                                   F.data == AppButtons.categories_data.CREATE_CATEGORIES.name)
    router.message.register(create_category_handler, CategoryState.GET_NAME)
    router.callback_query.register(pick_removing_category_handler,
                                   F.data == AppButtons.categories_data.DELETE_CATEGORIES.name)
    router.callback_query.register(del_category, CategoryCD.filter(F.operation == CategoryOperation.DEL))
    router.callback_query.register(select_update_category,
                                   F.data == AppButtons.categories_data.UPDATE_CATEGORIES.name)
    router.callback_query.register(select_category, CategoryCD.filter(F.operation == CategoryOperation.UDP))
    router.message.register(upd_category, UpdateCategoryState.WAIT_CATEGORY_DATA)

    return router
