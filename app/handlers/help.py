from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings
from app.models import User

router = Router()


@router.callback_query(F.data == "menu:help")
async def help_menu(cb: CallbackQuery, db_user: User | None) -> None:
    contact = (
        f"👤 Admin: @{settings.support_username}\n"
        if settings.support_username
        else ""
    )
    text = (
        "📞 <b>Yordam</b>\n\n"
        "Savol yoki muammoingiz bo'lsa, biz bilan bog'laning:\n"
        f"{contact}"
        "🕐 Ish vaqti: 9:00 - 21:00\n\n"
        "Ko'p so'raladigan savollar:\n"
        "• <b>To'lov qildim, fayl kelmadi?</b> — Karta to'lovida admin "
        "tasdiqlagach fayl avtomatik yuboriladi. Biroz kuting.\n"
        "• <b>Faylni qayta yuklab olsam bo'ladimi?</b> — Ha, 📚 Xaridlarim "
        "bo'limidan istalgan vaqt.\n"
        "• <b>Qanday to'layman?</b> — ⭐ Stars yoki 💳 Karta orqali."
    )
    b = InlineKeyboardBuilder()
    if settings.support_username:
        b.button(text="✍️ Adminga yozish", url=f"https://t.me/{settings.support_username}")
    b.button(text="⬅️ Orqaga", callback_data="menu:home")
    b.adjust(1)
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()
