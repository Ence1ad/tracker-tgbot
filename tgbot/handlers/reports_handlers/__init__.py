from aiogram import F, Router

from tgbot.keyboards.app_buttons import AppButtons


def register_report_handlers() -> Router:
    from .menu_report import get_report_options
    from .weekly_report import get_weekly_report

    router = Router()
    router.callback_query.register(get_report_options, F.data == AppButtons.general_data.REPORTS_BTN.name)
    router.callback_query.register(get_weekly_report, F.data == AppButtons.reports_data.WEEKLY_REPORT_BTN.name)

    return router
