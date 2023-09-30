from aiogram import F, Router


def register_categories_handlers() -> Router:
    """
    The register_categories_handlers function is a router that handles all the categories related callbacks.
    It registers handlers for:
        - displaying the main menu of categories;
        - displaying all the user's categories;
        - prompting for a new categories name to be created/updated;
        - creating/updating/deleting a category;

    :return: A router object
    """
    from .delete_category import delete_category_handler
    from .create_category import prompt_new_category_handler, create_category_handler
    from .read_categories import display_categories, categories_main_menu_handler
    from .update_category import upd_category_name, prompt_category_name
    from tgbot.keyboards.app_buttons import AppButtons
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation
    from tgbot.utils.states import CategoryState

    router = Router()

    router.callback_query.register(categories_main_menu_handler, F.data.in_(
        (AppButtons.general_data.ACTIONS_BTN.name,
        AppButtons.categories_data.UPDATE_CATEGORIES.name,
        AppButtons.categories_data.DELETE_CATEGORIES.name))
                                   )
    router.callback_query.register(display_categories, (F.data == AppButtons.general_data.CATEGORIES_BTN.name)
                                   | (F.data == AppButtons.categories_data.USER_CATEGORIES.name))
    router.callback_query.register(prompt_new_category_handler,
                                   F.data == AppButtons.categories_data.CREATE_CATEGORIES.name)
    router.message.register(create_category_handler, CategoryState.GET_NAME, F.text)
    router.callback_query.register(prompt_category_name, CategoryCD.filter(F.operation == CategoryOperation.UPD))
    router.message.register(upd_category_name, CategoryState.WAIT_CATEGORY_DATA, F.text)
    router.callback_query.register(delete_category_handler, CategoryCD.filter(F.operation == CategoryOperation.DEL))

    return router
