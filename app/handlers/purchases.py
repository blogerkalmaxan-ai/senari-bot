from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.locales import t
from app.models import User
from app.repositories.catalog import CatalogRepository
from app.repositories.purchase import PurchaseRepository
from app.services.delivery import deliver_scenario

router = Router()


def _lang(db_user: User | None) -> str:
    return db_user.lang if db_user else "uz"


@router.callback_query(F.data == "menu:purchases")
async def my_purchases(cb: CallbackQuery, session, db_user: User | None) -> None:
    lang = _lang(db_user)
    if not db_user:
        await cb.answer(t("purchases_empty", lang), show_alert=True)
        return
    repo = PurchaseRepository(session)
    items = await repo.list_for_user(db_user.id)
    if not items:
        await cb.answer(t("purchases_empty", lang), show_alert=True)
        return

    b = InlineKeyboardBuilder()
    lines = [t("purchases_title", lang), ""]
    for p in items:
        date = p.created_at.strftime("%d.%m.%Y")
        lines.append(f"• {p.scenario.title} — {int(p.price)} so'm ({date})")
        b.button(
            text=f"⬇️ {p.scenario.title[:30]}",
            callback_data=f"dl:{p.scenario_id}",
        )
    b.button(text=t("back_btn", lang), callback_data="menu:home")
    b.adjust(1)
    await cb.message.edit_text("\n".join(lines), reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("dl:"))
async def download(cb: CallbackQuery, bot: Bot, session, db_user: User | None) -> None:
    lang = _lang(db_user)
    sc_id = int(cb.data.split(":")[1])
    purchases = PurchaseRepository(session)
    if not db_user or not await purchases.owns(db_user.id, sc_id):
        await cb.answer("❌", show_alert=True)
        return
    catalog = CatalogRepository(session)
    scenario = await catalog.get_scenario(sc_id)
    if scenario:
        await deliver_scenario(bot, session, cb.from_user.id, scenario)
    await cb.answer(t("download_btn", lang))
