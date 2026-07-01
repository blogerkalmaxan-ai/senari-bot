from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Scenario

PAGE_SIZE = 5


class CatalogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_categories(self) -> list[Category]:
        res = await self.session.execute(
            select(Category).order_by(Category.sort_order, Category.id)
        )
        return list(res.scalars().all())

    async def get_category(self, cat_id: int) -> Category | None:
        return await self.session.get(Category, cat_id)

    async def get_scenario(self, scenario_id: int) -> Scenario | None:
        sc = await self.session.get(Scenario, scenario_id)
        return sc if sc and sc.is_active else None

    async def list_by_category(
        self, cat_id: int, page: int = 0
    ) -> tuple[list[Scenario], int]:
        base = select(Scenario).where(
            Scenario.category_id == cat_id, Scenario.is_active.is_(True)
        )
        total = await self.session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        res = await self.session.execute(
            base.order_by(Scenario.id)
            .offset(page * PAGE_SIZE)
            .limit(PAGE_SIZE)
        )
        return list(res.scalars().all()), int(total or 0)

    async def create_scenario(self, **fields) -> Scenario:
        sc = Scenario(**fields)
        self.session.add(sc)
        await self.session.commit()
        await self.session.refresh(sc)
        return sc

    async def update_scenario(self, scenario: Scenario, **fields) -> Scenario:
        for k, v in fields.items():
            setattr(scenario, k, v)
        await self.session.commit()
        await self.session.refresh(scenario)
        return scenario

    async def search(self, query: str, page: int = 0) -> tuple[list[Scenario], int]:
        like = f"%{query.lower()}%"
        cond = or_(
            func.lower(Scenario.title).like(like),
            func.lower(Scenario.keywords).like(like),
        )
        base = select(Scenario).where(Scenario.is_active.is_(True), cond)
        total = await self.session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        res = await self.session.execute(
            base.order_by(Scenario.id).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
        )
        return list(res.scalars().all()), int(total or 0)
