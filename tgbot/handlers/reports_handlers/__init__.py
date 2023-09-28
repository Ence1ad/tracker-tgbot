from aiogram import F, Router

from tgbot.keyboards.app_buttons import AppButtons


def register_report_handlers() -> Router:
    """
    The register_report_handlers function is a router that handles the report menu and weekly report.
        It has two handlers: main_menu_reports_handler and get_weekly_report.
        The first one is responsible for handling the reports button in the main menu, while
        the second one handles getting a weekly report.

    :return: The router object

    """
    from .menu_report import main_menu_reports_handler
    from .weekly_report import get_weekly_report

    router = Router()
    router.callback_query.register(main_menu_reports_handler, F.data == AppButtons.general_data.REPORTS_BTN.name)
    router.callback_query.register(get_weekly_report, F.data == AppButtons.reports_data.WEEKLY_REPORT_BTN.name)

    return router
