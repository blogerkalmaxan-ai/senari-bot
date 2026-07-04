import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.config import settings
from app.handlers import admin, card_payment, catalog, help, menu, payment, premium, purchases, start
from app.middlewares.db import DbSessionMiddleware
from app.models.base import Base, engine
import app.models  # noqa: F401

logging.basicConfig(level=logging.INFO)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Baza tayyor")
    try:
        from app.seed import seed
        await seed()
    except Exception as e:
        logging.warning("Seed skip: %s", e)


async def main() -> None:
    await init_db()
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        redis = Redis.from_url(redis_url)
    else:
        redis = Redis(host=settings.redis_host, port=settings.redis_port)
    storage = RedisStorage(redis=redis)
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)
    dp.update.outer_middleware(DbSessionMiddleware())
    dp.include_router(admin.router)
    dp.include_router(premium.router)
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(payment.router)
    dp.include_router(card_payment.router)
    dp.include_router(help.router)
    dp.include_router(purchases.router)
    dp.include_router(menu.router)
    logging.info("Senari.uz bot ishga tushdi")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
