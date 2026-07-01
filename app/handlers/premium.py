from aiogram import Bot, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings
from app.models import User
from app.repositories.premium import (
    PREMIUM_PLANS,
    PremiumRepository,
    ReferralRepository,
)

router = Router()


def _lang(u: User | None) -> str:
    return u.lang if u else "uz"


@router.message(CommandStart(deep_link=True))
async def start_with_ref(
    message: Message, command: CommandObject, session, db_user: User | None
) -> None:
    arg = command.args or ""
    if arg.startswith("ref_") and db_user:
        try:
            referrer = int(arg[4:])
            await ReferralRepository(session).attach(db_user, referrer)
        except ValueError:
            pass

    from app.handlers.start import show_main_menu
    from app.keyboards.common import lang_kb
    from app.locales import t

    if db_user and db_user.phone:
        await show_main_menu(message, _lang(db_user))
    else:
        await message.answer(t("choose_lang"), reply_markup=lang_kb())


@router.callback_query(F.data == "menu:premium")
async def premium_menu(cb: CallbackQuery, db_user: User | None) -> None:
    lang = _lang(db_user)
    b = InlineKeyboardBuilder()
    labels = {1: "1 oy", 3: "3 oy", 6: "6 oy", 12: "12 oy"}
    for months, price in PREMIUM_PLANS.items():
        b.button(
            text=f"{labels[months]} — {price} so'm",
            callback_data=f"prem:{months}",
        )
    b.button(text="⬅️ Orqaga", callback_data="menu:home")
    b.adjust(1)
    status = ""
    if db_user and db_user.is_premium and db_user.premium_until:
        status = f"\n\n✅ Premium: {db_user.premium_until.strftime('%d.%m.%Y')} gacha"
    text = (
        "⭐ <b>Premium obuna</b>\n\n"
        "• Cheksiz yuklab olish\n"
        "• Yangi senariylar birinchi bo'lib\n"
        "• Maxsus chegirmalar\n"
        "• Premium belgisi" + status
    )
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("prem:"))
async def buy_premium(cb: CallbackQuery, bot: Bot) -> None:
    months = int(cb.data.split(":")[1])
    price = PREMIUM_PLANS[months]
    stars = max(1, round(price / 1000))
    await bot.send_invoice(
        chat_id=cb.from_user.id,
        title=f"Premium {months} oy",
        description=f"Senari.uz Premium obuna — {months} oy",
        payload=f"premium:{months}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"Premium {months} oy", amount=stars)],
    )
    await cb.answer()


@router.callback_query(F.data == "menu:profile")
async def profile(cb: CallbackQuery, bot: Bot, db_user: User | None) -> None:
    lang = _lang(db_user)
    me = await bot.get_me()
    ref_link = f"https://t.me/{me.username}?start=ref_{cb.from_user.id}"
    prem = "✅" if (db_user and db_user.is_premium) else "❌"
    text = (
        "👤 <b>Profil</b>\n\n"
        f"Ism: {db_user.name if db_user else '-'}\n"
        f"Premium: {prem}\n"
        f"👥 Taklif qilganlar: {db_user.referral_count if db_user else 0}\n\n"
        f"🔗 Referal havolangiz:\n{ref_link}"
    )
    b = InlineKeyboardBuilder()
    b.button(text="🌐 Til / Язык / Language", callback_data="setlang")
    b.button(text="⬅️ Orqaga", callback_data="menu:home")
    b.adjust(1)
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data == "setlang")
async def choose_lang(cb: CallbackQuery) -> None:
    from app.keyboards.common import lang_kb

    await cb.message.edit_text(
        "Tilni tanlang / Выберите язык / Choose a language:",
        reply_markup=lang_kb(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("lang:"))
async def apply_lang(cb: CallbackQuery, users, db_user) -> None:
    lang = cb.data.split(":")[1]
    if db_user:
        await users.update(db_user, lang=lang)
    from app.keyboards.common import main_menu_kb
    from app.locales import t

    await cb.message.edit_text(
        t("main_menu", lang), reply_markup=main_menu_kb(lang)
    )
    await cb.answer("✅")
