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
    WEEKLY_REPORT_BTN: str = '🗓 Weekly report'


class SettingsButtonsData(Enum):
    LANGUAGE: str = '🌏 Language'
    RUSSIA: str = '🇷🇺 Russian'
    X_RUSSIA: str = '[X] 🇷🇺 Russian'
    ENGLISH: str = '🇬🇧 English'
    X_ENGLISH: str = '[X] 🇬🇧 English'

    @classmethod
    async def en_language_menu(cls) -> dict[str:str]:
        buttons_data = {cls.RUSSIA.name: cls.RUSSIA.value,
                        cls.X_ENGLISH.name: cls.ENGLISH.value}
        return buttons_data

    @classmethod
    async def ru_language_menu(cls) -> dict[str:str]:
        buttons_data = {cls.X_RUSSIA.name: cls.RUSSIA.value,
                        cls.ENGLISH.name: cls.ENGLISH.value}
        return buttons_data

    @classmethod
    async def settings_menu(cls) -> dict[str:str]:
        buttons_data = {cls.LANGUAGE.name: cls.LANGUAGE.value}
        return buttons_data