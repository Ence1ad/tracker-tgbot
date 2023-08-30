from aiogram import F, Router


def register_categories_handlers() -> Router:
    from .delete_category import select_remove_category, del_category
    from .new_category import new_category, get_category_name_from_user
    from .show_categories import display_categories
    from .update_category import select_update_category, upd_category, select_category

    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation
    from tgbot.utils.states import CategoryState, UpdateCategoryState

    router = Router()

    router.callback_query.register(display_categories, (F.data == 'categories_btn') | (F.data == 'user_categories'))
    router.callback_query.register(new_category, F.data == 'create_categories')
    router.message.register(get_category_name_from_user, CategoryState.GET_NAME)
    router.callback_query.register(select_remove_category, F.data == 'delete_categories')
    router.callback_query.register(del_category, CategoryCD.filter(F.operation == CategoryOperation.DEL))
    router.callback_query.register(select_update_category, F.data == 'update_categories')
    router.callback_query.register(select_category, CategoryCD.filter(F.operation == CategoryOperation.UDP))
    router.message.register(upd_category, UpdateCategoryState.WAIT_CATEGORY_DATA)

    return router
