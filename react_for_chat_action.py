

# @bot.on(events.ChatAction)
# async def chat_action(event):
#     if event.user_joined:
#         user_entity = event.user.id
#         chat_entity = event.chat
#
#         await event.get_input_user()
#         print(event.user)
#
#         if user_entity.username is not None:
#             greeting = '@' + user_entity.username
#         else:
#             greeting = user_entity.first_name
#
#         await bot.send_message(
#             entity= await bot.get_entity(PeerUser(user_entity.id)),
#
#             message=f'Привет, {greeting}, как твои дела?'
#         )