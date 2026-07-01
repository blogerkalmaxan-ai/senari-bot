from aiogram import Bot, F, Router
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from app.locales import t
from app.models import Payment, PaymentStatus, User
from app.repositories.catalog import CatalogRepository
from app.repositories.purchase import PurchaseRepository
from app.services.delivery import deliver_scenario

router = Router()

# Telegram Stars uses currency "XTR" and an empty provider_token.
STARS_CURRENCY = "XTR"


def price_to_stars(price: float) -> int:
    """Convert som price to Stars amount.
    Adjust this ratio to your pricing. Here: ~1000 som = 1 Star, min 1."""
    return max(1, round(float(price) / 1000))


def _lang(db_user: User | None) -> str:
    return db_user.lang if db_user else "uz"


@router.callback_query(F.data.startswith("buy:"))
async def start_payment(
    cb: CallbackQuery, bot: Bot, session, db_user: User | None
) -> None:
    lang = _lang(db_user)
    sc_id = int(cb.data.split(":")[1])
    catalog = CatalogRepository(session)
    purchases = PurchaseRepository(session)

    scenario = await catalog.get_scenario(sc_id)
    if not scenario:
        await cb.answer("❌", show_alert=True)
        return

    if db_user and await purchases.owns(db_user.id, sc_id):
        await cb.answer(t("already_owned", lang), show_alert=True)
        return

    stars = price_to_stars(scenario.price)
    await bot.send_invoice(
        chat_id=cb.from_user.id,
        title=t("invoice_title", lang, title=scenario.title)[:32],
        description=t("invoice_desc", lang, title=scenario.title)[:255],
        payload=f"scenario:{scenario.id}",
        provider_token="",  # empty for Stars
        currency=STARS_CURRENCY,
        prices=[LabeledPrice(label=scenario.title[:32], amount=stars)],
    )
    await cb.answer()


@router.pre_checkout_query()
async def pre_checkout(pcq: PreCheckoutQuery, bot: Bot) -> None:
    # Always approve here; real provider checks happen for Click/Payme later.
    await bot.answer_pre_checkout_query(pcq.id, ok=True)


@router.message(F.successful_payment)
async def on_success(
    message: Message, bot: Bot, session, db_user: User | None
) -> None:
    lang = _lang(db_user)
    sp = message.successful_payment
    payload = sp.invoice_payload

    # Premium purchase
    if payload.startswith("premium:") and db_user:
        from app.repositories.premium import PremiumRepository

        months = int(payload.split(":")[1])
        await PremiumRepository(session).activate(db_user, months)
        await message.answer(
            f"⭐ Premium {months} oyga faollashtirildi! "
            f"{db_user.premium_until.strftime('%d.%m.%Y')} gacha."
        )
        return

    try:
        sc_id = int(payload.split(":")[1])
    except (IndexError, ValueError):
        return

    catalog = CatalogRepository(session)
    purchases = PurchaseRepository(session)
    scenario = await catalog.get_scenario(sc_id)
    if not scenario or not db_user:
        return

    # idempotency: skip if already recorded
    if not await purchases.owns(db_user.id, sc_id):
        session.add(
            Payment(
                user_id=db_user.id,
                scenario_id=sc_id,
                provider="stars",
                provider_charge_id=sp.telegram_payment_charge_id,
                amount=scenario.price,
                status=PaymentStatus.paid,
            )
        )
        await purchases.add(db_user.id, sc_id, scenario.price)

    await message.answer(t("pay_success", lang))
    await deliver_scenario(bot, session, message.chat.id, scenario)
