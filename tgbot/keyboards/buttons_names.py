from dataclasses import dataclass


@dataclass
class ActionsButtons:
    user_actions: str = '📋 List of actions'
    create_actions: str = '🆕 Create action'
    update_actions: str = '🆙 Change action'
    delete_actions: str = '🗑 Delete action'

    @classmethod
    async def action_menu_buttons(cls) -> dict[str:str]:
        buttons_dict = {
            'user_actions': cls.user_actions,
            'create_actions': cls.create_actions,
            'update_actions': cls.update_actions,
            'delete_actions': cls.delete_actions,
        }
        return buttons_dict

    @classmethod
    async def new_action(cls) -> dict[str:str]:
        buttons_dict = {'create_actions': cls.create_actions}
        return buttons_dict


@dataclass
class CategoriesButtons:
    user_categories: str = '🗂 List of categories'
    create_categories: str = '🆕 Create category'
    update_categories: str = '🆙 Change category'
    delete_categories: str = '🗑 Delete category'

    @classmethod
    async def category_menu_buttons(cls) -> dict[str:str]:
        buttons_dict = {
            'user_categories': cls.user_categories,
            'create_categories': cls.create_categories,
            'update_categories': cls.update_categories,
            'delete_categories': cls.delete_categories
        }
        return buttons_dict

    @classmethod
    async def new_category(cls) -> dict[str:str]:
        buttons_dict = {'create_categories': cls.create_categories}
        return buttons_dict

    @classmethod
    async def category_limit_menu(cls) -> dict[str:str]:
        buttons_dict = {'delete_categories': cls.delete_categories, }
        return buttons_dict


@dataclass
class TrackersButtons:
    new_tracker_btn: str = '▶️ Start tracking'
    delete_tracker_btn: str = '🗑 Delete trackers'
    launched_btn: str = '⏹ Stop tracking'
    update_tracker_btn: str = '⏳ Get Duration'

    @classmethod
    async def tracker_menu_start(cls) -> dict[str:str]:
        buttons_dict = {
            'new_tracker_btn': cls.new_tracker_btn,
            'delete_tracker_btn': cls.delete_tracker_btn
        }
        return buttons_dict

    @classmethod
    async def tracker_menu_stop(cls) -> dict[str:str]:
        buttons_dict = {
            'launched_btn': cls.launched_btn,
            'update_tracker_btn': cls.update_tracker_btn,
            'delete_tracker_btn': cls.delete_tracker_btn
        }
        return buttons_dict


@dataclass
class ReportsButtons:
    weekly_report_btn = '🗓 Weekly report'

    @classmethod
    async def report_menu(cls) -> dict[str:str]:
        buttons_dict = {'weekly_report_btn': cls.weekly_report_btn}
        return buttons_dict


@dataclass
class CustomButtons:
    actions_btn: str = '🎬 Actions'
    categories_btn: str = '🗄 Categories'
    reports_btn: str = '📊 Reports'
    trackers_btn: str = '⏱ Trackers'
    yes_btn = '🟩 Yes'
    no_btn = '🟥 No'

    exit_btn = '⬅️ exit'
    cancel_btn = '🚫 cancel'

    @classmethod
    async def main_menu_buttons(cls) -> dict[str:str]:
        buttons_dict = {
            'actions_btn': cls.actions_btn,
            'categories_btn': cls.categories_btn,
            'reports_btn': cls.reports_btn,
            'trackers_btn': cls.trackers_btn
        }
        return buttons_dict

    @classmethod
    async def yes_no_menu(cls) -> dict[str:str]:
        buttons_dict = {'yes_btn': cls.yes_btn,
                        'no_btn': cls.no_btn}
        return buttons_dict

    @classmethod
    async def action_limit_menu(cls) -> dict[str:str]:
        buttons_dict = {'actions_btn': cls.actions_btn,
                        'delete_actions': ActionsButtons.delete_actions}
        return buttons_dict
