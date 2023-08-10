from aiogram.types import Message


from db.users.user import NewUser
from db.users.users_commands import create_user, check_user_in_db
from ..keyboards.start_kb import start_custom_kb
from ..utils.answer_text import user_in_db_text, new_user_text


async def command_start_handler(message: Message) -> None:
    """
    Function react to tap on "/start" command. Function check if user exist in db,
    function just return some answer as message, else create user in db and return answer as message.
    :param message: Message
    :return: Coroutine[Any]
    """

    # await message.answer(f"Hello, <b>{message.from_user.id}!</b>")

    user_id: int = message.from_user.id
    user_obj: NewUser = await _get_sender_data(message)
    user_id_from_db: str | None = await check_user_in_db(user_id)

    # Get keyboard
    start_markup = await start_custom_kb()
    # Check if sender already in DB
    if user_id == user_id_from_db:
        await message.answer(text=user_in_db_text, reply_markup=start_markup)

    else:
        # Create new user in DB
        await create_user(user_obj)
        await message.answer(text=new_user_text, reply_markup=start_markup)


async def _get_sender_data(message: Message) -> NewUser:
    """
    Function get user data from sender and return new NewUser instance.
    :param message:
    :return: NewUser(user_id=user.id,...)
    """
    user_obj: NewUser = NewUser(user_id=message.from_user.id,
                                first_name=message.from_user.first_name,
                                last_name=message.from_user.last_name,
                                username=message.from_user.username,
                                )
    return user_obj
