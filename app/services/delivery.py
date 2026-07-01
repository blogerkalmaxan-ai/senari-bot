import os

from aiogram import Bot
from aiogram.types import FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Scenario


async def deliver_scenario(
    bot: Bot, session: AsyncSession, chat_id: int, scenario: Scenario
) -> None:
    """Send the scenario document. Reuse cached file_id if available,
    otherwise upload from disk and cache the returned file_id."""
    caption = f"📄 <b>{scenario.title}</b>"

    if scenario.file_id:
        await bot.send_document(chat_id, scenario.file_id, caption=caption)
        return

    path = os.path.join(
        settings.files_dir,
        f"{scenario.id}.{scenario.file_format.value}",
    )
    if not os.path.exists(path):
        await bot.send_message(
            chat_id,
            "⚠️ Fayl topilmadi. Administrator bilan bog'laning: 📞 Yordam",
        )
        return

    msg = await bot.send_document(chat_id, FSInputFile(path), caption=caption)
    if msg.document:
        scenario.file_id = msg.document.file_id
        await session.commit()
