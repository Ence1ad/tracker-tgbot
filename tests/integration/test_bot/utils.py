from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from tests.utils import MAIN_USER_ID

TEST_USER = User(
    id=MAIN_USER_ID,
    is_bot=False,
    first_name='Test'
)

TEST_CHAT = Chat(
    id=12,
    type='private',
    username=TEST_USER.username,
    first_name=TEST_USER.first_name,
    last_name=TEST_USER.last_name,
)

TEST_MESSAGE = Message(message_id=123, date=datetime.now(), chat=TEST_CHAT, text='')


def get_message(text: str, chat=TEST_CHAT, from_user=None, **kwargs):
    """Get message update for tests."""
    return Message(
        message_id=123,
        date=datetime.now(),
        chat=chat,
        from_user=from_user,
        sender_chat=TEST_CHAT,
        text=text,
        **kwargs
    )


def get_chat(
    chat_id: int = None,
    chat_type: str = 'private',
    title: str = 'TEST_TITLE',
    username: str = TEST_CHAT.username,
    **kwargs
) -> Chat:
    """Get chat object for tests."""
    return Chat(
        id=chat_id,
        type=chat_type,
        title=title,
        username=username,
        first_name=TEST_USER.first_name,
        last_name=TEST_USER.last_name,
        **kwargs
    )


def get_callback_query(
    data: str | CallbackData, from_user=None, message=None, **kwargs
):
    """Get callback query update for tests."""

    return CallbackQuery(
        id='test',
        from_user=from_user,
        chat_instance='test',
        message=message or TEST_MESSAGE,
        data=data,
        **kwargs
    )


def get_update(
    message: Message = None, callback_query: CallbackQuery = None, **kwargs
):
    """Get mocked update for tests."""

    return Update(
        update_id=187,
        message=message,
        callback_query=callback_query,
        **kwargs
    )
