from dataclasses import dataclass

from tgbot.keyboards.buttons_classes import CategoriesButtonsData, GeneralButtonsData,\
    ActionsButtonsData, TrackersButtonsData, ReportsButtonsData, SettingsButtonsData


@dataclass
class AppButtons:
    """Initialize the AppButtons data class."""

    categories_btn_source: type[CategoriesButtonsData] = CategoriesButtonsData
    general_btn_source: type[GeneralButtonsData] = GeneralButtonsData
    actions_btn_source: type[ActionsButtonsData] = ActionsButtonsData
    trackers_btn_source: type[TrackersButtonsData] = TrackersButtonsData
    reports_btn_source: type[ReportsButtonsData] = ReportsButtonsData
    settings_btn_source: type[SettingsButtonsData] = SettingsButtonsData
    settings_btn_list = list(SettingsButtonsData.__members__.keys())

