from dataclasses import dataclass
from enum import Enum


class ActionsButtonsData(Enum):
    USER_ACTIONS: str = '📋 List of actions'
    CREATE_ACTIONS: str = '🆕 Create action'
    UPDATE_ACTIONS: str = '🆙 Change action'
    DELETE_ACTIONS: str = '🗑 Delete action'


class CategoriesButtonsData(Enum):
    USER_CATEGORIES: str = '🗂 List of categories'
    CREATE_CATEGORIES: str = '🆕 Create category'
    UPDATE_CATEGORIES: str = '🆙 Change category'
    DELETE_CATEGORIES: str = '🗑 Delete category'


class GeneralButtonsData(Enum):
    ACTIONS_BTN: str = '🎬 Actions'
    CATEGORIES_BTN: str = '🗄 Categories'
    REPORTS_BTN: str = '📊 Reports'
    TRACKERS_BTN: str = '⏱ Trackers'
    YES_BTN: str = '🟩 Yes'
    NO_BTN: str = '🟥 No'
    EXIT_BTN: str = '⬅️ exit'
    CANCEL_BTN: str = '🚫 cancel'


class TrackersButtonsData(Enum):
    START_TRACKER_BTN: str = '▶️ Start tracking'
    DELETE_TRACKER_BTN: str = '🗑 Delete trackers'
    STOP_TRACKER_BTN: str = '⏹ Stop tracking'
    DURATION_TRACKER_BTN: str = '⏳ Get Duration'


class ReportsButtonsData(Enum):
    WEEKLY_REPORT_BTN = '🗓 Weekly report'


@dataclass
class AppButtons:
    categories_data: CategoriesButtonsData = CategoriesButtonsData
    general_data: GeneralButtonsData = GeneralButtonsData
    actions_data: ActionsButtonsData = ActionsButtonsData
    trackers_data: TrackersButtonsData = TrackersButtonsData
    reports_data: ReportsButtonsData = ReportsButtonsData

    @classmethod
    async def action_menu_buttons(cls) -> dict[str:str]:
        buttons_data = {
            cls.actions_data.USER_ACTIONS.name: cls.actions_data.USER_ACTIONS.value,
            cls.actions_data.CREATE_ACTIONS.name: cls.actions_data.CREATE_ACTIONS.value,
            cls.actions_data.UPDATE_ACTIONS.name: cls.actions_data.UPDATE_ACTIONS.value,
            cls.actions_data.DELETE_ACTIONS.name: cls.actions_data.DELETE_ACTIONS.value,
        }
        return buttons_data

    @classmethod
    async def new_action(cls) -> dict[str:str]:
        buttons_data = {cls.actions_data.CREATE_ACTIONS.name: cls.actions_data.CREATE_ACTIONS.value}
        return buttons_data

    @classmethod
    async def category_menu_buttons(cls) -> dict[str:str]:
        buttons_data = {
            cls.categories_data.USER_CATEGORIES.name: cls.categories_data.USER_CATEGORIES.value,
            cls.categories_data.CREATE_CATEGORIES.name: cls.categories_data.CREATE_CATEGORIES.value,
            cls.categories_data.UPDATE_CATEGORIES.name: cls.categories_data.UPDATE_CATEGORIES.value,
            cls.categories_data.DELETE_CATEGORIES.name: cls.categories_data.DELETE_CATEGORIES.value
        }
        return buttons_data

    @classmethod
    async def new_category(cls) -> dict[str:str]:
        buttons_data = {cls.categories_data.CREATE_CATEGORIES.name: cls.categories_data.CREATE_CATEGORIES.value}
        return buttons_data

    @classmethod
    async def category_limit_menu(cls) -> dict[str:str]:
        buttons_data = {cls.categories_data.DELETE_CATEGORIES.name: cls.categories_data.DELETE_CATEGORIES.value}
        return buttons_data

    @classmethod
    async def main_menu_buttons(cls) -> dict[str:str]:
        buttons_data = {
            cls.general_data.ACTIONS_BTN.name: cls.general_data.ACTIONS_BTN.value,
            cls.general_data.CATEGORIES_BTN.name: cls.general_data.CATEGORIES_BTN.value,
            cls.general_data.REPORTS_BTN.name: cls.general_data.REPORTS_BTN.value,
            cls.general_data.TRACKERS_BTN.name: cls.general_data.TRACKERS_BTN.value
        }
        return buttons_data

    @classmethod
    async def yes_no_menu(cls) -> dict[str:str]:
        buttons_data = {cls.general_data.YES_BTN.name: cls.general_data.YES_BTN.value,
                        cls.general_data.NO_BTN.name: cls.general_data.NO_BTN.value}
        return buttons_data

    @classmethod
    async def action_limit_menu(cls) -> dict[str:str]:
        buttons_data = {
            cls.general_data.ACTIONS_BTN.name: cls.general_data.ACTIONS_BTN.value,
            cls.actions_data.DELETE_ACTIONS.name: cls.actions_data.DELETE_ACTIONS.value
        }
        return buttons_data

    @classmethod
    async def tracker_menu_start(cls) -> dict[str:str]:
        buttons_data = {
            cls.trackers_data.START_TRACKER_BTN.name: cls.trackers_data.START_TRACKER_BTN.value,
            cls.trackers_data.DELETE_TRACKER_BTN.name: cls.trackers_data.DELETE_TRACKER_BTN.value
        }
        return buttons_data

    @classmethod
    async def tracker_menu_stop(cls) -> dict[str:str]:
        buttons_data = {
            cls.trackers_data.STOP_TRACKER_BTN.name: cls.trackers_data.STOP_TRACKER_BTN.value,
            cls.trackers_data.DURATION_TRACKER_BTN.name: cls.trackers_data.DURATION_TRACKER_BTN.value,
            cls.trackers_data.DELETE_TRACKER_BTN.name: cls.trackers_data.DELETE_TRACKER_BTN.value
        }
        return buttons_data

    @classmethod
    async def report_menu(cls) -> dict[str:str]:
        buttons_data = {cls.reports_data.WEEKLY_REPORT_BTN.name: cls.reports_data.WEEKLY_REPORT_BTN.value}
        return buttons_data
