import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.config import settings
from app.handlers import admin, catalog, payment, premium, purchases, start
from app.middlewares.db import DbSessionMiddleware

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    redis = Redis(host=settings.redis_host, port=settings.redis_port)
    storage = RedisStorage(redis=redis)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=storage)

    # DB session + user injected on every update
    dp.update.outer_middleware(DbSessionMiddleware())

    dp.include_router(admin.router)
    dp.include_router(premium.router)
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(payment.router)
    dp.include_router(purchases.router)

    logging.info("Senari.uz bot ishga tushdi")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
