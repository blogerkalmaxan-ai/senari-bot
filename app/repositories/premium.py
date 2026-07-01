from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Favorite, PromoCode, Review, User

PREMIUM_PLANS = {  # months -> price (som)
    1: 19000,
    3: 49000,
    6: 89000,
    12: 149000,
}


class PremiumRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def activate(self, user: User, months: int) -> User:
        now = datetime.now(timezone.utc)
        base = user.premium_until if user.premium_until and user.premium_until > now else now
        user.premium_until = base + timedelta(days=30 * months)
        user.is_premium = True
        await self.session.commit()
        await self.session.refresh(user)
        return user


class ReferralRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def attach(self, new_user: User, referrer_tg_id: int) -> None:
        if new_user.referred_by or new_user.tg_id == referrer_tg_id:
            return
        referrer = await self.session.scalar(
            select(User).where(User.tg_id == referrer_tg_id)
        )
        if not referrer:
            return
        new_user.referred_by = referrer_tg_id
        referrer.referral_count += 1
        await self.session.commit()


class PromoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate(self, code: str) -> PromoCode | None:
        promo = await self.session.scalar(
            select(PromoCode).where(
                func.lower(PromoCode.code) == code.lower(),
                PromoCode.is_active.is_(True),
            )
        )
        if not promo:
            return None
        if promo.max_uses and promo.used_count >= promo.max_uses:
            return None
        return promo

    async def consume(self, promo: PromoCode) -> None:
        promo.used_count += 1
        await self.session.commit()


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def toggle(self, user_id: int, scenario_id: int) -> bool:
        existing = await self.session.scalar(
            select(Favorite).where(
                Favorite.user_id == user_id, Favorite.scenario_id == scenario_id
            )
        )
        if existing:
            await self.session.delete(existing)
            await self.session.commit()
            return False
        self.session.add(Favorite(user_id=user_id, scenario_id=scenario_id))
        await self.session.commit()
        return True

    async def list_ids(self, user_id: int) -> list[int]:
        res = await self.session.execute(
            select(Favorite.scenario_id).where(Favorite.user_id == user_id)
        )
        return [r[0] for r in res.all()]


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_id: int, scenario_id: int, stars: int, comment: str | None):
        self.session.add(
            Review(user_id=user_id, scenario_id=scenario_id, stars=stars, comment=comment)
        )
        await self.session.commit()

    async def avg_for(self, scenario_id: int) -> float:
        avg = await self.session.scalar(
            select(func.avg(Review.stars)).where(Review.scenario_id == scenario_id)
        )
        return round(float(avg), 1) if avg else 0.0
