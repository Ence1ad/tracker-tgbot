from aiogram import F, Router


def register_categories_handlers() -> Router:
    """Register category-related handlers in a router.

    This function configures and registers various category-related handlers in a Router
     instance.

    Handler Descriptions:
    - 'categories_main_menu_handler': Handles category-related actions from the main
    menu.
    - 'display_categories': Displays the user's categories and related actions.
    - 'prompt_new_category_handler': Prompts the user to enter a new category name for
     creation.
    - 'create_category_handler': Creates a new category based on the user's input.
    - 'prompt_category_name': Prompts the user to enter a new category name for
     updating.
    - 'upd_category_name': Updates a category's name based on the user's input.
    - 'delete_category_handler': Deletes a category.
    :return: Router: A configured Router object with registered category handlers.
    """
    from .delete_category import delete_category_handler
    from .create_category import prompt_new_category_handler, create_category_handler
    from .read_categories import display_categories, categories_main_menu_handler
    from .update_category import upd_category_name, prompt_category_name
    from tgbot.keyboards.app_buttons import AppButtons
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation
    from tgbot.utils.states import CategoryState

    router = Router()

    router.callback_query.register(
        categories_main_menu_handler, F.data.in_(
            (
                AppButtons.general_btn_source.ACTIONS_BTN.name,
                AppButtons.categories_btn_source.UPDATE_CATEGORIES.name,
                AppButtons.categories_btn_source.DELETE_CATEGORIES.name,
                AppButtons.trackers_btn_source.START_TRACKER_BTN.name
            )
        )
    )
    router.callback_query.register(display_categories, (
                F.data == AppButtons.general_btn_source.CATEGORIES_BTN.name) |
                (F.data == AppButtons.categories_btn_source.USER_CATEGORIES.name))
    router.callback_query.register(
        prompt_new_category_handler,
        F.data == AppButtons.categories_btn_source.CREATE_CATEGORIES.name
    )
    router.message.register(create_category_handler, CategoryState.GET_NAME, F.text)
    router.callback_query.register(prompt_category_name, CategoryCD.filter(
        F.operation == CategoryOperation.UPD))
    router.message.register(upd_category_name, CategoryState.WAIT_CATEGORY_DATA, F.text)
    router.callback_query.register(delete_category_handler, CategoryCD.filter(
        F.operation == CategoryOperation.DEL))

    return router
