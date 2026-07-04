from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.catalog import categories_kb
from app.keyboards.common import menu_labels
from app.locales import t
from app.models import User
from app.repositories.catalog import CatalogRepository

router = Router()


def _lang(u: User | None) -> str:
    return u.lang if u else "uz"


def _match(text: str) -> str:
    result = {}
    for lang in ("uz", "ru", "en"):
        for key, label in menu_labels(lang).items():
            result[label] = key
    return result.get(text, "")


@router.message(F.text)
async def bottom_menu(
    message: Message, bot: Bot, state, session, db_user: User | None
) -> None:
    section = _match(message.text)
    if not section:
        return
    lang = _lang(db_user)

    if section == "catalog":
        cats = await CatalogRepository(session).list_categories()
        await message.answer(
            t("categories_title", lang), reply_markup=categories_kb(cats, lang)
        )

    elif section == "search":
        from app.handlers.catalog import Search

        await message.answer(t("search_prompt", lang))
        await state.set_state(Search.query)

    elif section == "purchases":
        from app.repositories.purchase import PurchaseRepository

        if not db_user:
            await message.answer(t("purchases_empty", lang))
            return
        items = await PurchaseRepository(session).list_for_user(db_user.id)
        if not items:
            await message.answer(t("purchases_empty", lang))
            return
        b = InlineKeyboardBuilder()
        lines = [t("purchases_title", lang), ""]
        for p in items:
            date = p.created_at.strftime("%d.%m.%Y")
            lines.append(f"• {p.scenario.title} — {int(p.price)} so'm ({date})")
            b.button(text=f"⬇️ {p.scenario.title[:30]}", callback_data=f"dl:{p.scenario_id}")
        b.adjust(1)
        await message.answer("\n".join(lines), reply_markup=b.as_markup())

    elif section == "premium":
        from app.repositories.premium import PREMIUM_PLANS

        b = InlineKeyboardBuilder()
        labels = {1: "1 oy", 3: "3 oy", 6: "6 oy", 12: "12 oy"}
        for months, price in PREMIUM_PLANS.items():
            b.button(text=f"{labels[months]} — {price} so'm", callback_data=f"prem:{months}")
        b.adjust(1)
        status = ""
        if db_user and db_user.is_premium and db_user.premium_until:
            status = f"\n\n✅ Premium: {db_user.premium_until.strftime('%d.%m.%Y')} gacha"
        await message.answer(
            "⭐ <b>Premium obuna</b>\n\n"
            "• Cheksiz yuklab olish\n"
            "• Yangi senariylar birinchi bo'lib\n"
            "• Maxsus chegirmalar\n"
            "• Premium belgisi" + status,
            reply_markup=b.as_markup(),
        )

    elif section == "help":
        from app.config import settings

        contact = f"👤 Admin: @{settings.support_username}\n" if settings.support_username else ""
        b = InlineKeyboardBuilder()
        if settings.support_username:
            b.button(text="✍️ Adminga yozish", url=f"https://t.me/{settings.support_username}")
            b.adjust(1)
        await message.answer(
            "📞 <b>Yordam</b>\n\n"
            "Savol yoki muammoingiz bo'lsa, biz bilan bog'laning:\n"
            f"{contact}"
            "🕐 Ish vaqti: 9:00 - 21:00\n\n"
            "• To'lov qildim, fayl kelmadi? — Admin tasdiqlagach fayl avtomatik yuboriladi.\n"
            "• Qayta yuklab olsam bo'ladimi? — Ha, 📚 Xaridlarim bo'limidan.\n"
            "• Qanday to'layman? — ⭐ Stars yoki 💳 Karta orqali.",
            reply_markup=b.as_markup() if settings.support_username else None,
        )

    elif section == "profile":
        me = await bot.get_me()
        ref_link = f"https://t.me/{me.username}?start=ref_{message.from_user.id}"
        prem = "✅" if (db_user and db_user.is_premium) else "❌"
        pc = 0
        if db_user:
            from app.repositories.purchase import PurchaseRepository

            pc = len(await PurchaseRepository(session).list_for_user(db_user.id))
        b = InlineKeyboardBuilder()
        b.button(text="🌐 Til / Язык / Language", callback_data="setlang")
        b.adjust(1)
        await message.answer(
            "👤 <b>Profil</b>\n\n"
            f"Ism: {db_user.name if db_user else '-'}\n"
            f"Premium: {prem}\n"
            f"🛍 Xaridlar: {pc} ta\n"
            f"👥 Taklif qilganlar: {db_user.referral_count if db_user else 0}\n\n"
            f"🔗 Referal havolangiz:\n{ref_link}",
            reply_markup=b.as_markup(),
        )
