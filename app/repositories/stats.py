from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Payment, PaymentStatus, Scenario, User


class StatsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def users_count(self) -> int:
        return int(await self.session.scalar(select(func.count(User.id))) or 0)

    async def premium_count(self) -> int:
        return int(
            await self.session.scalar(
                select(func.count(User.id)).where(User.is_premium.is_(True))
            )
            or 0
        )

    async def scenarios_count(self) -> int:
        return int(
            await self.session.scalar(select(func.count(Scenario.id))) or 0
        )

    async def _revenue_since(self, since: datetime) -> tuple[int, float]:
        stmt = select(
            func.count(Payment.id), func.coalesce(func.sum(Payment.amount), 0)
        ).where(Payment.status == PaymentStatus.paid, Payment.created_at >= since)
        row = (await self.session.execute(stmt)).one()
        return int(row[0]), float(row[1])

    async def today(self) -> tuple[int, float]:
        start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return await self._revenue_since(start)

    async def last_30_days(self) -> tuple[int, float]:
        since = datetime.now(timezone.utc) - timedelta(days=30)
        return await self._revenue_since(since)
