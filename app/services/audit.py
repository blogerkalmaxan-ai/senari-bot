from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


async def log_action(
    session: AsyncSession, actor_tg_id: int, action: str, details: str | None = None
) -> None:
    session.add(
        AuditLog(actor_tg_id=actor_tg_id, action=action, details=details)
    )
    await session.commit()
