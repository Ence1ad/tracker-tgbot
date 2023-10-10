welcome_group_text = Welcome to our group!
farewell_group_text =  has been removed from the group!
canceling_text = Your action has been canceled
exit_text = See you soon!
options_text = Select the button
select_lang_text = Select a language
set_lang_text = ✅ The Russian language was set!
settings_not_change_text = ❌ Already installed ❗️
use_bot_text = To use the bot, you need to register in the group:
help_unknown_command_text = Sorry, I don't recognize that command. Please use '/help' to see available commands
help_invalid_command_format_text = Invalid command format. Use '/help_<command>' to get help for specific commands.
valid_data_text = ❗️ Please provide correct data ❗️
throttling_text = ❗️ You are sending messages too quickly. Please wait. ❗️

# for command_start_handler func
user_in_db_text = 👋🏼 Greetings, my friend, 🤖 I am very glad to see you!
new_user_text = Hello friend! What can I do for you?

# text for categories handlers
new_category_text = Write the name of the category below.
added_new_category_text = ✅ You have successfully added the new category
show_categories_text = Your categories:
empty_categories_text = You don't have any categories yet
select_category_text = Select the category
selected_category = Selected category -> {$category_name}{$new_line}{$actions_list_text}
rm_category_text = ✅ The category has been deleted!
upd_category_text = ✅ The category name has been updated to {$new_category_name}
correct_category_text = Please write the correct category name. {$new_line}
                        The category name is a text, no more than 30 characters!
categories_is_fake_text = Choose the right category
category_exists_text = ❌ Failed to update the category name! {$new_line}❗️ The category with the name - {$new_category_name} already exists ❗️

category_limit_text =  ❗️ You have reached the limit of the number of categories - {$category_limit} ❗️
valid_category_name_text = ❌ Failed to update the category name! {$new_line}❗️ The name must consist of letters ❗️
valid_new_category_name_text = ❌ Failed to create new category! {$new_line}❗️ The name must consist of letters ❗️

# text for actions handlers
new_action_text = Write the name of the action below.
show_action_text = Your actions for the category -> {$category_name}{$new_line}{$actions_list_text}
to_delete_action_text = Select the action to delete
select_action_text = Select the action
to_update_action_text = Select the action to update
empty_actions_text = You don't have any actions yet
rm_action_text = ✅ You have deleted the action -> {$action_name}
upd_action_text = ✅ You have updated the name of your action
first_start_text = Please use "setting" button for adjust your action tracker
correct_action_text = Please write the correct action name. The action name is a text, no more than 30 characters!
action_limit_text = ❗️ You have reached the limit of the number of actions - {$action_limit} for this category. ❗️
action_exists_text = The action name - {$new_action_name} already exists!

action_not_exists_text = ❗️ Choose the right action ❗️
added_new_action_text = ✅ You successfully added new action - {$new_action_valid_name}
valid_action_name = ❌ Failed to update the action name! {$new_line}❗️ The name must consist of letters ❗️
new_valid_action_name = ❌ Failed to create new action! {$new_line}❗️ The name must consist of letters ❗️

# text for tracker handlers
new_tracker_text = ✅ You have started tracking action -> {$action_name}
select_category_4_tracker = Selected category -> {$category_name}. {$new_line} Select the action!
not_launched_tracker_text = You don't have any launched tracker yet!
already_launch_tracker_text = You already have a running tracker:
empty_category_actions_text = ❗️ Make sure you have created action for the category ❗️
answer_stop_tracker_text = Do you want to stop the tracker?
stop_tracker_text = ✅ The tracker was stopped:
daily_tracker_text = Delete daily tracker
empty_stopped_tracker_text = ❗️ You don't have any trackers stopped yet ❗️
delete_tracker_text = ✅ You have deleted the tracker
just_one_tracker = You can't run more than one tracker at a time. Do you want to stop the tracker?
not_enough_data_text = I can't create a tracker. The data is not defined.
already_delete_tracker_text = You have already deleted the tracker
too_long_tracker = the tracker for this action was automatically stopped and deleted! The tracker can't work longer than 23 hours!
tracker_daily_limit_text = You have reached the daily limit of the number of trackers
# for reports handlers
send_report_text = This is your weekly report
empty_trackers_text = You don't have any trackers for this week

# for started_tracker_text function
started_tracker_title = Started tracker:
category_title = 🗄 Selected category
action_title = 🎬 Selected action
action_duration = ⏱ Duration

# keyboards:
# ActionsButtonsData
USER_ACTIONS = 📋 List of actions
CREATE_ACTIONS = 🆕 Create action
UPDATE_ACTIONS = 🆙 Change action
DELETE_ACTIONS = 🗑 Delete action


# CategoriesButtonsData
USER_CATEGORIES = 🗂 List of categories
CREATE_CATEGORIES = 🆕 Create category
UPDATE_CATEGORIES = 🆙 Change category
DELETE_CATEGORIES = 🗑 Delete category


# GeneralButtonsData:
ACTIONS_BTN = 🎬 Actions
CATEGORIES_BTN = 🗄 Categories
REPORTS_BTN = 📊 Reports
TRACKERS_BTN = ⏱ Trackers
YES_BTN = 🟩 Yes
NO_BTN = 🟥 No
EXIT_BTN = ⬅️ exit
CANCEL_BTN = 🚫 cancel


# TrackersButtonsData
START_TRACKER_BTN = ▶️ Start tracking
DELETE_TRACKER_BTN = 🗑 Delete trackers
STOP_TRACKER_BTN = ⏹ Stop tracking
DURATION_TRACKER_BTN = ⏳ Get Duration


# ReportsButtonsData
WEEKLY_REPORT_BTN = 🗓 Weekly report

# SettingsButtonsData
LANGUAGE = 🌏 Language
RUSSIA = 🇷🇺 Russian
X_RUSSIA = [X] 🇷🇺 Russian
ENGLISH = 🇬🇧 English
X_ENGLISH = [X] 🇬🇧 English