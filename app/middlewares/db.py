from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.models.base import async_session
from app.repositories.user import UserRepository


class DbSessionMiddleware(BaseMiddleware):
    """Opens a session per update and loads the User (if already registered)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with async_session() as session:
            data["session"] = session
            repo = UserRepository(session)
            data["users"] = repo

            tg_user = data.get("event_from_user")
            if tg_user:
                data["db_user"] = await repo.get_by_tg_id(tg_user.id)

            return await handler(event, data)
