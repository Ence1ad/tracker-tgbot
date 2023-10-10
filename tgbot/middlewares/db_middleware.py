from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class DbSessionMiddleware(BaseMiddleware):
    """
    Initialize the DbSessionMiddleware.

    :param session_pool: An async sessionmaker for creating database sessions.
    :type session_pool: async_sessionmaker[AsyncSession]

    This middleware is responsible for managing database sessions using the provided session pool.
    """
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Awaitable[Any]:
        """
        Handle incoming events with database session management.

        :param handler: The event handler function to be called.
        :type handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]

        :param event: The incoming Telegram event.
        :type event: TelegramObject

        :param data: Data associated with the event.
        :type data: Dict[str, Any]

        :return: The result of the event handler.
        :rtype: Awaitable[Any]

        This method is called when an event is received by the Telegram bot. It manages the lifecycle of
        a database session by acquiring and associating it with the event data, then passing control to
        the provided event handler. Once the handler has completed, the session is automatically closed.

        """
        async with self.session_pool() as session:
            data["db_session"] = session
            return await handler(event, data)
