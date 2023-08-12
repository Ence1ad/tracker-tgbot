import datetime

from aiogram.types import CallbackQuery

# for command_start_handler func
user_in_db_text = f"Hello friend! I'm glad to see you again!"
new_user_text = f"Hello friend! What can I do for you?"

# for get_categories_options func
categories_options_text = f"Select the button"

# for new_category func
new_category_text = f"Write category name"

# for get_category_name_from_user func
added_new_category_text = 'You successfully added new category'

# for show_categories func
show_categories_text = "This is your categories:"
empty_categories_text = f"You don't have any categories yet"

# for remove and update category funcs
select_category_text = f"Select the category"
rm_category_text = "You deleted your category: "

upd_category_text = "You updated your category: "

# for get_category_name_from_user func
added_new_action_text = 'You successfully added new action'

# for new_action func
new_action_text = f"Write action name"

# for display_actions func
show_action_text = "This is your actions:"
select_action_text = "Select the actions:"
empty_actions_text = f"You don't have any actions yet"

rm_action_text = "You deleted your action: "

upd_action_text = "You updated your action: "

new_tracker_text = f"You launch tracking action: "

options_text = f"Select the button"

first_start_text = 'Please use setting button for adjust your action tracker'

not_launched_tracker_text = "You don't have any launched tracker"
launch_tracker_text = "Launched tracker:"
already_launch_tracker_text = "You already have a tracker running:"
answer_stop_tracker = "\n\nDo you want to stop tracker?"
stop_tracker = "Tracker stopped:"


async def traker_text(call: CallbackQuery, tracker):
    action_name = tracker.Tracker.actions.action_name,
    category_name = tracker.Tracker.actions.actions_categories.category_name,
    launch_time = tracker.Tracker.track_start,
    call_datetime: datetime = call.message.date
    duration = str(call_datetime - launch_time[0]).split('.')[0]
    text = f"\n\rcategory: {category_name[0]}\n\raction:  {action_name[0]}\n\rduration: {duration}"
    return text
