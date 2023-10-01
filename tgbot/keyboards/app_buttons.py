from dataclasses import dataclass

from tgbot.keyboards.buttons_classes import CategoriesButtonsData, GeneralButtonsData, ActionsButtonsData, \
    TrackersButtonsData, ReportsButtonsData, SettingsButtonsData


@dataclass
class AppButtons:
    categories_btn_source: CategoriesButtonsData = CategoriesButtonsData
    general_btn_source: GeneralButtonsData = GeneralButtonsData
    actions_btn_source: ActionsButtonsData = ActionsButtonsData
    trackers_btn_source: TrackersButtonsData = TrackersButtonsData
    reports_btn_source: ReportsButtonsData = ReportsButtonsData
    settings_btn_source: SettingsButtonsData = SettingsButtonsData
    settings_btn_list = list(map(str, [attr.name for attr in settings_btn_source]))




