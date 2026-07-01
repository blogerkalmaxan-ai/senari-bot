import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI, Request

from app.config import settings
from app.models import Payment, PaymentStatus, User
from app.models.base import async_session
from app.repositories.catalog import CatalogRepository
from app.repositories.purchase import PurchaseRepository
from app.repositories.user import UserRepository
from app.services import click
from app.services.delivery import deliver_scenario

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Senari.uz Webhooks")

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode="HTML"),
)


async def _form_dict(request: Request) -> dict:
    form = await request.form()
    return {k: form[k] for k in form}


@app.post("/click/prepare")
async def click_prepare(request: Request):
    data = await _form_dict(request)
    async with async_session() as session:
        return await click.handle_prepare(session, data)


@app.post("/click/complete")
async def click_complete(request: Request):
    data = await _form_dict(request)
    async with async_session() as session:
        result = await click.handle_complete(session, data)
        # On success, record purchase + deliver file
        if result.get("error") == click.SUCCESS:
            payment = await session.get(Payment, int(data["merchant_trans_id"]))
            if payment and payment.status == PaymentStatus.paid and payment.scenario_id:
                purchases = PurchaseRepository(session)
                if not await purchases.owns(payment.user_id, payment.scenario_id):
                    await purchases.add(
                        payment.user_id, payment.scenario_id, payment.amount
                    )
                users = UserRepository(session)
                user = await session.get(User, payment.user_id)
                catalog = CatalogRepository(session)
                scenario = await catalog.get_scenario(payment.scenario_id)
                if user and scenario:
                    try:
                        await deliver_scenario(bot, session, user.tg_id, scenario)
                    except Exception as e:  # delivery shouldn't break the callback
                        logging.error("Delivery failed: %s", e)
        return result


@app.get("/health")
async def health():
    return {"status": "ok"}
