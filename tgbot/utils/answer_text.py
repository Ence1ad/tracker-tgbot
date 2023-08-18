import datetime

from aiogram.types import CallbackQuery

options_text = f"Select the button"

# for command_start_handler func
user_in_db_text = f"Hello friend! I'm glad to see you again!"
new_user_text = f"Hello friend! What can I do for you?"

# text for categories handlers
categories_options_text = f"Select the button"
new_category_text = f"Write category name"
added_new_category_text = 'You have successfully added the new category'
show_categories_text = "This is your categories:"
empty_categories_text = f"You don't have any categories yet"
select_category_text = f"Select the category"
rm_category_text = "You have deleted your category: "
upd_category_text = "You have updated your category: "
correct_category_text = 'Please write the correct category name. ' \
                        'The category name is a text, no more than 30 characters!'

# for get_category_name_from_user func
added_new_action_text = 'You successfully added new action'

# text for actions handlers
new_action_text = f"Write action name"
show_action_text = "Your actions for category "
select_action_text = "Select the actions"
empty_actions_text = f"You don't have any actions yet"
rm_action_text = "You deleted your action:"
upd_action_text = "You updated your action:"
first_start_text = 'Please use setting button for adjust your action tracker'
correct_action_text = "Please write the correct action name. The action name is a text, no more than 30 characters!"
action_limit_text = f"You have reached the limit of the number of actions for this category.\n" \
                    f"Please delete any action or change the category"
action_exists_text = "already exists!\nPlease write another name:"

# text for tracker handlers
new_tracker_text = f"You have started tracking action: "
not_launched_tracker_text = "You don't have any launched tracker yet!"
launch_tracker_text = f"Started tracker:\n\r"
already_launch_tracker_text = "You already have a running tracker:\n\r"
answer_stop_tracker_text = "\n\nDo you want to stop tracker?"
stop_tracker_text = "Tracker stopped:\n\r"
daily_tracker_text = "Delete daily tracker"
empty_tracker_text = "You don't have any trackers yet"
delete_tracker_text = "You deleted the tracker"


async def traker_text(call: CallbackQuery, tracker) -> str:
    text = []
    call_datetime: datetime = call.message.date
    for track in tracker:
        launch_time = track.track_start
        category_name = "🗄:" + track.category_name
        action_name = "🎬:" + track.action_name
        duration = "⏱:" + str(call_datetime - launch_time).split('.')[0]
        text += [category_name, action_name, duration]
    text = '\n\r'.join(text)
    return text


# for reports handlers
send_report_text = "This is your weekly report"
empty_trackers_text = "You don't have any trackers"

# for create_report.py
xlsx_title = "Weekly Report.xlsx"
