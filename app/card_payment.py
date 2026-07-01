from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings
from app.models import User
from app.repositories.catalog import CatalogRepository
from app.repositories.purchase import PurchaseRepository
from app.services.delivery import deliver_scenario

router = Router()


class CardPay(StatesGroup):
    waiting_receipt = State()


def _lang(u: User | None) -> str:
    return u.lang if u else "uz"


@router.callback_query(F.data.startswith("card:"))
async def card_start(
    cb: CallbackQuery, state: FSMContext, session, db_user: User | None
) -> None:
    sc_id = int(cb.data.split(":")[1])
    catalog = CatalogRepository(session)
    purchases = PurchaseRepository(session)
    scenario = await catalog.get_scenario(sc_id)
    if not scenario:
        await cb.answer("❌", show_alert=True)
        return
    if db_user and await purchases.owns(db_user.id, sc_id):
        await cb.answer("✅ Bu senariy sizda bor.", show_alert=True)
        return

    if not settings.card_number:
        await cb.answer(
            "Karta to'lovi hozircha sozlanmagan. ⭐ Stars bilan urinib ko'ring.",
            show_alert=True,
        )
        return

    await state.update_data(sc_id=sc_id)
    await state.set_state(CardPay.waiting_receipt)
    text = (
        "💳 <b>Karta orqali to'lov</b>\n\n"
        f"Karta: <code>{settings.card_number}</code>\n"
        f"Egasi: {settings.card_holder}\n"
        f"Summa: <b>{int(scenario.price)} so'm</b>\n\n"
        f"Senariy: {scenario.title}\n\n"
        "To'lovni amalga oshiring va <b>chek / skrinshotni</b> shu yerga yuboring. "
        "Admin tasdiqlagach, fayl avtomatik yuboriladi."
    )
    await cb.message.answer(text)
    await cb.answer()


@router.message(CardPay.waiting_receipt, F.photo)
async def receipt_received(
    message: Message, state: FSMContext, bot: Bot, db_user: User | None
) -> None:
    data = await state.get_data()
    sc_id = data.get("sc_id")
    await state.clear()

    await message.answer(
        "✅ Chek qabul qilindi! Admin tekshiradi va tez orada faylni yuboradi."
    )

    user_tag = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    caption = (
        "🔔 <b>Yangi karta to'lovi</b>\n\n"
        f"Mijoz: {user_tag} (ID {message.from_user.id})\n"
        f"Senariy ID: {sc_id}"
    )
    b = InlineKeyboardBuilder()
    b.button(text="✅ Tasdiqlash", callback_data=f"appr:{message.from_user.id}:{sc_id}")
    b.button(text="❌ Rad etish", callback_data=f"rej:{message.from_user.id}")
    b.adjust(2)

    for admin_id in settings.admin_id_list:
        try:
            await bot.send_photo(
                admin_id,
                message.photo[-1].file_id,
                caption=caption,
                reply_markup=b.as_markup(),
            )
        except Exception:
            pass


@router.message(CardPay.waiting_receipt)
async def receipt_not_photo(message: Message) -> None:
    await message.answer("Iltimos, chek/skrinshotni <b>rasm</b> sifatida yuboring.")


@router.callback_query(F.data.startswith("appr:"))
async def approve(cb: CallbackQuery, bot: Bot, session) -> None:
    if cb.from_user.id not in settings.admin_id_list:
        await cb.answer("Ruxsat yo'q", show_alert=True)
        return
    _, buyer_id, sc_id = cb.data.split(":")
    buyer_id, sc_id = int(buyer_id), int(sc_id)

    from app.repositories.user import UserRepository

    users = UserRepository(session)
    buyer = await users.get_by_tg_id(buyer_id)
    catalog = CatalogRepository(session)
    purchases = PurchaseRepository(session)
    scenario = await catalog.get_scenario(sc_id)

    if not buyer or not scenario:
        await cb.answer("Xatolik: mijoz yoki senariy topilmadi", show_alert=True)
        return

    if not await purchases.owns(buyer.id, sc_id):
        await purchases.add(buyer.id, sc_id, scenario.price)

    try:
        await bot.send_message(buyer_id, "✅ To'lovingiz tasdiqlandi! Faylingiz yuborilmoqda...")
        await deliver_scenario(bot, session, buyer_id, scenario)
    except Exception:
        pass

    await cb.message.edit_caption(
        caption=(cb.message.caption or "") + "\n\n✅ TASDIQLANDI"
    )
    await cb.answer("Tasdiqlandi ✅")


@router.callback_query(F.data.startswith("rej:"))
async def reject(cb: CallbackQuery, bot: Bot) -> None:
    if cb.from_user.id not in settings.admin_id_list:
        await cb.answer("Ruxsat yo'q", show_alert=True)
        return
    buyer_id = int(cb.data.split(":")[1])
    try:
        await bot.send_message(
            buyer_id,
            "❌ To'lovingiz tasdiqlanmadi. Iltimos, admin bilan bog'laning: 📞 Yordam",
        )
    except Exception:
        pass
    await cb.message.edit_caption(
        caption=(cb.message.caption or "") + "\n\n❌ RAD ETILDI"
    )
    await cb.answer("Rad etildi")
