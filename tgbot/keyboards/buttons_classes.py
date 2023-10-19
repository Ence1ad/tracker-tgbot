from enum import Enum


class ActionsButtonsData(Enum):
    """Enum to represent a set of action-related buttons."""

    USER_ACTIONS: str = '📋 List of actions'
    CREATE_ACTIONS: str = '🆕 Create action'
    UPDATE_ACTIONS: str = '🆙 Change action'
    DELETE_ACTIONS: str = '🗑 Delete action'

    @classmethod
    async def action_menu_buttons(cls: type['ActionsButtonsData']) -> dict[str, str]:
        """Get a dictionary of action-related buttons.

        :return: dict[str, str]: A dictionary containing action-related button names
        and values.
        """
        buttons_data: dict[str, str] = {
            cls.USER_ACTIONS.name: cls.USER_ACTIONS.value,
            cls.CREATE_ACTIONS.name: cls.CREATE_ACTIONS.value,
            cls.UPDATE_ACTIONS.name: cls.UPDATE_ACTIONS.value,
            cls.DELETE_ACTIONS.name: cls.DELETE_ACTIONS.value,
        }
        return buttons_data

    @classmethod
    async def new_action(cls: type['ActionsButtonsData']) -> dict[str, str]:
        """Get a dictionary containing the "Create action" button.

        :return: dict[str, str]: A dictionary containing the "Create action" button.
        """
        buttons_data: dict[str, str] = {
            cls.CREATE_ACTIONS.name: cls.CREATE_ACTIONS.value
        }
        return buttons_data


class CategoriesButtonsData(Enum):
    """Enum for category-related buttons."""

    USER_CATEGORIES: str = '🗂 List of categories'
    CREATE_CATEGORIES: str = '🆕 Create category'
    UPDATE_CATEGORIES: str = '🆙 Change category'
    DELETE_CATEGORIES: str = '🗑 Delete category'

    @classmethod
    async def category_menu_buttons(cls: type['CategoriesButtonsData']
                                    ) -> dict[str, str]:
        """Get a dictionary of category menu buttons.

        :return: dict[str, str]: A dictionary of category menu buttons.
        """
        buttons_data: dict[str, str] = {
            cls.USER_CATEGORIES.name: cls.USER_CATEGORIES.value,
            cls.CREATE_CATEGORIES.name: cls.CREATE_CATEGORIES.value,
            cls.UPDATE_CATEGORIES.name: cls.UPDATE_CATEGORIES.value,
            cls.DELETE_CATEGORIES.name: cls.DELETE_CATEGORIES.value
        }
        return buttons_data

    @classmethod
    async def new_category(cls: type['CategoriesButtonsData']) -> dict[str, str]:
        """Get a dictionary for creating a new category.

        :return: dict[str, str]: A dictionary for creating a new category.
        """
        buttons_data: dict[str, str] = {
            cls.CREATE_CATEGORIES.name: cls.CREATE_CATEGORIES.value
        }
        return buttons_data


class GeneralButtonsData(Enum):
    """Enum for general buttons."""

    ACTIONS_BTN: str = '🎬 Actions'
    CATEGORIES_BTN: str = '🗄 Categories'
    REPORTS_BTN: str = '📊 Reports'
    TRACKERS_BTN: str = '⏱ Trackers'
    YES_BTN: str = '🟩 Yes'
    NO_BTN: str = '🟥 No'
    EXIT_BTN: str = '⬅️ exit'
    CANCEL_BTN: str = '🚫 cancel'

    @classmethod
    async def main_menu_buttons(cls: type['GeneralButtonsData']) -> dict[str, str]:
        """Get a dictionary of main menu buttons.

        :return: dict[str, str]: A dictionary of main menu buttons.
        """
        buttons_data: dict[str, str] = {
            cls.ACTIONS_BTN.name: cls.ACTIONS_BTN.value,
            cls.CATEGORIES_BTN.name: cls.CATEGORIES_BTN.value,
            cls.REPORTS_BTN.name: cls.REPORTS_BTN.value,
            cls.TRACKERS_BTN.name: cls.TRACKERS_BTN.value
        }
        return buttons_data

    @classmethod
    async def yes_no_menu(cls: type['GeneralButtonsData']) -> dict[str, str]:
        """Get a dictionary of "Yes" and "No" buttons.

        :return: dict[str, str]: A dictionary of "Yes" and "No" buttons.
        """
        buttons_data: dict[str, str] = {cls.YES_BTN.name: cls.YES_BTN.value,
                                        cls.NO_BTN.name: cls.NO_BTN.value}
        return buttons_data


class TrackersButtonsData(Enum):
    """Enum for tracker-related buttons."""

    START_TRACKER_BTN: str = '▶️ Start tracking'
    DELETE_TRACKER_BTN: str = '🗑 Delete trackers'
    STOP_TRACKER_BTN: str = '⏹ Stop tracking'
    DURATION_TRACKER_BTN: str = '⏳ Get Duration'

    @classmethod
    async def tracker_menu_start(cls: type['TrackersButtonsData']) -> dict[str, str]:
        """Get a dictionary of tracker start menu buttons.

        :return: dict[str, str]: A dictionary of tracker start menu buttons.
        """
        buttons_data: dict[str, str] = {
            cls.START_TRACKER_BTN.name: cls.START_TRACKER_BTN.value,
            cls.DELETE_TRACKER_BTN.name: cls.DELETE_TRACKER_BTN.value
        }
        return buttons_data

    @classmethod
    async def tracker_menu_stop(cls: type['TrackersButtonsData']) -> dict[str, str]:
        """Get a dictionary of tracker stop menu buttons.

        :return: dict[str, str]: A dictionary of tracker stop menu buttons.
        """
        buttons_data: dict[str, str] = {
            cls.STOP_TRACKER_BTN.name: cls.STOP_TRACKER_BTN.value,
            cls.DURATION_TRACKER_BTN.name: cls.DURATION_TRACKER_BTN.value,
            cls.DELETE_TRACKER_BTN.name: cls.DELETE_TRACKER_BTN.value
        }
        return buttons_data


class ReportsButtonsData(Enum):
    """Enum for report-related buttons."""

    WEEKLY_REPORT_BTN: str = '🗓 Weekly report'

    @classmethod
    async def report_menu(cls: type['ReportsButtonsData']) -> dict[str, str]:
        """Get a dictionary of report menu buttons.

        :return: dict[str, str]: A dictionary of report menu buttons.
        """
        buttons_data: dict[str, str] = {
            cls.WEEKLY_REPORT_BTN.name: cls.WEEKLY_REPORT_BTN.value
        }
        return buttons_data


class SettingsButtonsData(Enum):
    """Enum for settings-related buttons."""

    LANGUAGE: str = '🌏 Language'
    RUSSIA: str = '🇷🇺 Russian'
    X_RUSSIA: str = '[X] 🇷🇺 Russian'
    ENGLISH: str = '🇬🇧 English'
    X_ENGLISH: str = '[X] 🇬🇧 English'

    @classmethod
    async def en_language_menu(cls: type['SettingsButtonsData']) -> dict[str, str]:
        """Get a dictionary of English language menu buttons.

        :return: dict[str, str]: A dictionary of English language menu buttons.
        """
        buttons_data: dict[str, str] = {
            cls.RUSSIA.name: cls.RUSSIA.value,
            cls.X_ENGLISH.name: cls.ENGLISH.value
        }
        return buttons_data

    @classmethod
    async def ru_language_menu(cls: type['SettingsButtonsData']) -> dict[str, str]:
        """Get a dictionary of Russian language menu buttons.

        :return: dict[str, str]: A dictionary of Russian language menu buttons.
        """
        buttons_data: dict[str, str] = {
            cls.X_RUSSIA.name: cls.RUSSIA.value,
            cls.ENGLISH.name: cls.ENGLISH.value
        }
        return buttons_data

    @classmethod
    async def settings_menu(cls: type['SettingsButtonsData']) -> dict[str, str]:
        """Get a dictionary of settings menu buttons.

        :return: dict[str, str]: A dictionary of settings menu buttons.
        """
        buttons_data: dict[str, str] = {
            cls.LANGUAGE.name: cls.LANGUAGE.value
        }
        return buttons_data
