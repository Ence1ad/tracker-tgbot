from aiogram import F

from .menu_report import get_report_options
from tgbot.keyboards.buttons_names import reports_btn


def register_report_handlers(router):
    router.callback_query.register(get_report_options, F.data == reports_btn)
    # router.callback_query.register(select_category_tracker, F.data == new_tracker_btn)