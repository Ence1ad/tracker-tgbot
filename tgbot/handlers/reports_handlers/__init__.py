from aiogram import F, Router


def register_report_handlers() -> Router:
    from .menu_report import get_report_options
    from .weekly_report import get_weekly_report

    router = Router()
    router.callback_query.register(get_report_options, F.data == 'reports_btn')
    router.callback_query.register(get_weekly_report, F.data == 'weekly_report_btn')

    return router
