from settings import LENGTH_ACTION_NAME_LIMIT

# Common
options_text = f"Select the button"
char_limit = f"\n\rThe limit on the length of the name is {LENGTH_ACTION_NAME_LIMIT} characters"
accept_only_text = "Please try again, I only accept text message"


# for command_start_handler func
user_in_db_text = f"Hello friend! I'm glad to see you again!"
new_user_text = f"Hello friend! What can I do for you?"

# text for categories handlers
categories_options_text = f"Select the button"
new_category_text = f"Write the name of the category below."
added_new_category_text = 'You have successfully added the new category'
show_categories_text = "This is your categories: "
empty_categories_text = f"You don't have any categories yet"
select_category_text = f"Select the category"
rm_category_text = "You have deleted your category: "
upd_category_text = "You have updated your category: "
correct_category_text = 'Please write the correct category name. ' \
                        'The category name is a text, no more than 30 characters!'
categories_is_fake_text = "Choose the right category"
category_exists_text = "category already exists!\nPlease write another name: "
category_limit_text = f"You have reached the limit of the number of categories for this category.\n" \
                    f"Please delete any categories"

# text for actions handlers
new_action_text = f"Write the name of the action below."
show_action_text = "Your actions for the category: "
to_delete_action_text = "Select the action to delete"
select_action_text = "Select the action"
to_update_action_text = "Select the action to update"
empty_actions_text = f"You don't have any actions yet"
rm_action_text = "You have deleted your action: "
upd_action_text = "You have updated the name of your action"
first_start_text = 'Please use setting button for adjust your action tracker'
correct_action_text = "Please write the correct action name. The action name is a text, no more than 30 characters!"
action_limit_text = f"You have reached the limit of the number of actions for this category.\n" \
                    f"Please delete any action or change the category"
action_exists_text = "action already exists!\nPlease write another name: "
action_not_exists_text = "Choose the right action"
added_new_action_text = 'You successfully added new action'

# text for tracker handlers
new_tracker_text = f"You have started tracking action: \n\r"
not_launched_tracker_text = "You don't have any launched tracker yet!"
launch_tracker_text = f"Started tracker:\n\r"
already_launch_tracker_text = "You already have a running tracker:\n\r"
answer_stop_tracker_text = "\n\nDo you want to stop tracker?"
stop_tracker_text = "Tracker stopped:\n\r"
daily_tracker_text = "Delete daily tracker"
empty_tracker_text = "You don't have any trackers yet"
delete_tracker_text = "You have deleted the tracker"
just_one_tracker = "You have only one tracker running. Do you want to stop the tracker?"
not_enough_data_text = "I can't create a tracker. The data is not defined."
already_delete_tracker_text = "You have already deleted the tracker"


# for reports handlers
send_report_text = "This is your weekly report"
empty_trackers_text = "You don't have any trackers for this week"

# for create_report.py
xlsx_title = "Weekly Report.xlsx"
