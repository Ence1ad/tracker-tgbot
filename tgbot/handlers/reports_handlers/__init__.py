from aiogram import F, Router

from tgbot.keyboards.app_buttons import AppButtons


def register_report_handlers() -> Router:
    """Register report-related callback handlers.

    This function creates and configures an instance of the Aiogram Router for handling
     callback queries related to reports.

    :return: Router: An Aiogram Router instance with registered callback handlers for
    report-related actions.
    """
    from .menu_report import main_menu_reports_handler
    from .weekly_report import get_weekly_report

    router = Router()
    router.callback_query.register(
        main_menu_reports_handler,
        F.data == AppButtons.general_btn_source.REPORTS_BTN.name
    )
    router.callback_query.register(
        get_weekly_report,
        F.data == AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name
    )

    return router
