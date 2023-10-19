from .common_handles import register_common_handlers
from .actions_handlers import register_actions_handlers
from .categories_handlers import register_categories_handlers
from .tracker_handlers import register_tracker_handlers
from .reports_handlers import register_report_handlers

__all__ = ['register_common_handlers', 'register_actions_handlers',
           'register_categories_handlers', 'register_tracker_handlers',
           'register_report_handlers']
