from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Purchase, Scenario


class PurchaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def owns(self, user_id: int, scenario_id: int) -> bool:
        res = await self.session.scalar(
            select(Purchase.id).where(
                Purchase.user_id == user_id, Purchase.scenario_id == scenario_id
            )
        )
        return res is not None

    async def add(self, user_id: int, scenario_id: int, price: float) -> Purchase:
        p = Purchase(user_id=user_id, scenario_id=scenario_id, price=price)
        self.session.add(p)
        await self.session.commit()
        await self.session.refresh(p)
        return p

    async def list_for_user(self, user_id: int) -> list[Purchase]:
        res = await self.session.execute(
            select(Purchase)
            .where(Purchase.user_id == user_id)
            .options(selectinload(Purchase.scenario))
            .order_by(Purchase.created_at.desc())
        )
        return list(res.scalars().all())
