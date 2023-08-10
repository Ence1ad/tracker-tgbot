from telethon.events import NewMessage
from telethon.tl.types import PeerUser, ReplyInlineMarkup, User

from db.users.user import NewUser
from db.users.users_commands import create_user, check_user_in_db
from config import bot
from tgbot.keyboards.start_kb import start_kb


# @bot.on(events.NewMessage(pattern='/start'))
async def start(event: NewMessage.Event):
    """
    Function react to tap on "/start" command. Function check if user exist in db,
    function just return some answer as message, else create user in db and return answer as message.
    :param event: NewMessage.Event
    :return: Coroutine[Any]
    """
    user_id: PeerUser = event.peer_id
    user_obj: NewUser = await _get_sender_data(event)
    # Check if message came from user
    if isinstance(user_id, PeerUser):
        result: str | None = await check_user_in_db(user_id.user_id)
        # Get keyboard
        markup: ReplyInlineMarkup = await start_kb()
        # Check if sender already in DB
        if user_id.user_id == result:
            # Message for user.
            await bot.send_message(entity=user_id,
                                   message=f"Привет {user_obj.first_name} {user_obj.last_name}, "
                                           f"рад тебя снова видеть!",
                                   buttons=markup)
        else:
            # Create new user in DB
            await create_user(user_obj)
            #  Message for new user.
            await bot.send_message(entity=user_id,
                                   message=f"Приветствую {user_obj.first_name} {user_obj.last_name}, "
                                           f"так как вы у меня в гостях впервые, позвольте вас познакомить с "
                                           f"(в продолжение сообщения можно вставить контент)",
                                   buttons=markup)


async def _get_sender_data(event: NewMessage.Event) -> NewUser:
    """
    Function get user data from sender and return new NewUser instance.
    :param event:
    :return: NewUser(user_id=user.id,...)
    """
    user: User = event.sender
    user_obj: NewUser = NewUser(user_id=user.id,
                                first_name=user.first_name,
                                last_name=user.last_name,
                                username=user.username,
                                phone=user.phone
                                )
    return user_obj
