from enum import Enum
from typing import Type

class ActionsButtonsData(Enum):
    USER_ACTIONS: str = '📋 List of actions'
    CREATE_ACTIONS: str = '🆕 Create action'
    UPDATE_ACTIONS: str = '🆙 Change action'
    DELETE_ACTIONS: str = '🗑 Delete action'
    
    @classmethod
    async def action_menu_buttons(cls: Type['ActionsButtonsData']) -> dict[str:str]:
        buttons_data = {
            cls.USER_ACTIONS.name: cls.USER_ACTIONS.value,
            cls.CREATE_ACTIONS.name: cls.CREATE_ACTIONS.value,
            cls.UPDATE_ACTIONS.name: cls.UPDATE_ACTIONS.value,
            cls.DELETE_ACTIONS.name: cls.DELETE_ACTIONS.value,
        }
        return buttons_data

    @classmethod
    async def new_action(cls: Type['ActionsButtonsData']) -> dict[str:str]:
        buttons_data = {
            cls.CREATE_ACTIONS.name: cls.CREATE_ACTIONS.value
        }
        return buttons_data


class CategoriesButtonsData(Enum):
    USER_CATEGORIES: str = '🗂 List of categories'
    CREATE_CATEGORIES: str = '🆕 Create category'
    UPDATE_CATEGORIES: str = '🆙 Change category'
    DELETE_CATEGORIES: str = '🗑 Delete category'
    
    @classmethod
    async def category_menu_buttons(cls: Type['CategoriesButtonsData']) -> dict[str:str]:
        buttons_data = {
            cls.USER_CATEGORIES.name: cls.USER_CATEGORIES.value,
            cls.CREATE_CATEGORIES.name: cls.CREATE_CATEGORIES.value,
            cls.UPDATE_CATEGORIES.name: cls.UPDATE_CATEGORIES.value,
            cls.DELETE_CATEGORIES.name: cls.DELETE_CATEGORIES.value
        }
        return buttons_data

    @classmethod
    async def new_category(cls: Type['CategoriesButtonsData']) -> dict[str:str]:
        buttons_data = {
            cls.CREATE_CATEGORIES.name: cls.CREATE_CATEGORIES.value
        }
        return buttons_data

    @classmethod
    async def category_limit_menu(cls: Type['CategoriesButtonsData']) -> dict[str:str]:
        buttons_data = {
            cls.DELETE_CATEGORIES.name: cls.DELETE_CATEGORIES.value
        }
        return buttons_data


class GeneralButtonsData(Enum):
    ACTIONS_BTN: str = '🎬 Actions'
    CATEGORIES_BTN: str = '🗄 Categories'
    REPORTS_BTN: str = '📊 Reports'
    TRACKERS_BTN: str = '⏱ Trackers'
    YES_BTN: str = '🟩 Yes'
    NO_BTN: str = '🟥 No'
    EXIT_BTN: str = '⬅️ exit'
    CANCEL_BTN: str = '🚫 cancel'
    
    @classmethod
    async def main_menu_buttons(cls: Type['GeneralButtonsData']) -> dict[str:str]:
        buttons_data = {
            cls.ACTIONS_BTN.name: cls.ACTIONS_BTN.value,
            cls.CATEGORIES_BTN.name: cls.CATEGORIES_BTN.value,
            cls.REPORTS_BTN.name: cls.REPORTS_BTN.value,
            cls.TRACKERS_BTN.name: cls.TRACKERS_BTN.value
        }
        return buttons_data

    @classmethod
    async def yes_no_menu(cls: Type['GeneralButtonsData']) -> dict[str:str]:
        buttons_data = {cls.YES_BTN.name: cls.YES_BTN.value,
                        cls.NO_BTN.name: cls.NO_BTN.value}
        return buttons_data


class TrackersButtonsData(Enum):
    START_TRACKER_BTN: str = '▶️ Start tracking'
    DELETE_TRACKER_BTN: str = '🗑 Delete trackers'
    STOP_TRACKER_BTN: str = '⏹ Stop tracking'
    DURATION_TRACKER_BTN: str = '⏳ Get Duration'
    
    @classmethod
    async def tracker_menu_start(cls: Type['TrackersButtonsData']) -> dict[str:str]:
        buttons_data = {
            cls.START_TRACKER_BTN.name: cls.START_TRACKER_BTN.value,
            cls.DELETE_TRACKER_BTN.name: cls.DELETE_TRACKER_BTN.value
        }
        return buttons_data

    @classmethod
    async def tracker_menu_stop(cls: Type['TrackersButtonsData']) -> dict[str:str]:
        buttons_data = {
            cls.STOP_TRACKER_BTN.name: cls.STOP_TRACKER_BTN.value,
            cls.DURATION_TRACKER_BTN.name: cls.DURATION_TRACKER_BTN.value,
            cls.DELETE_TRACKER_BTN.name: cls.DELETE_TRACKER_BTN.value
        }
        return buttons_data


class ReportsButtonsData(Enum):
    WEEKLY_REPORT_BTN: str = '🗓 Weekly report'
    # DAILY_REPORT_BTN: str = '🗓 Daily report'
    # MONTHLY_REPORT_BTN: str = '🗓 Monthly report'
    # YEARLY_REPORT_BTN: str = '🗓 Yearly report'

    @classmethod
    async def report_menu(cls: Type['ReportsButtonsData']) -> dict[str:str]:
        buttons_data = {cls.WEEKLY_REPORT_BTN.name: cls.WEEKLY_REPORT_BTN.value}
        return buttons_data


class SettingsButtonsData(Enum):
    LANGUAGE: str = '🌏 Language'
    RUSSIA: str = '🇷🇺 Russian'
    X_RUSSIA: str = '[X] 🇷🇺 Russian'
    ENGLISH: str = '🇬🇧 English'
    X_ENGLISH: str = '[X] 🇬🇧 English'

    @classmethod
    async def en_language_menu(cls: Type['SettingsButtonsData']) -> dict[str:str]:
        buttons_data = {cls.RUSSIA.name: cls.RUSSIA.value,
                        cls.X_ENGLISH.name: cls.ENGLISH.value}
        return buttons_data

    @classmethod
    async def ru_language_menu(cls: Type['SettingsButtonsData']) -> dict[str:str]:
        buttons_data = {cls.X_RUSSIA.name: cls.RUSSIA.value,
                        cls.ENGLISH.name: cls.ENGLISH.value}
        return buttons_data

    @classmethod
    async def settings_menu(cls: Type['SettingsButtonsData']) -> dict[str:str]:
        buttons_data = {cls.LANGUAGE.name: cls.LANGUAGE.value}
        return buttons_data