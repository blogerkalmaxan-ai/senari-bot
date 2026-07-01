from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models import FileFormat
from app.repositories.catalog import CatalogRepository
from app.repositories.stats import StatsRepository
from app.utils.admin_filter import IsAdmin

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class AddScenario(StatesGroup):
    category = State()
    title = State()
    description = State()
    price = State()
    file = State()
    cover = State()


def admin_menu_kb():
    b = InlineKeyboardBuilder()
    b.button(text="➕ Senariy qo'shish", callback_data="adm:add")
    b.button(text="📊 Statistika", callback_data="adm:stats")
    b.adjust(1)
    return b.as_markup()


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "adm:stats")
async def show_stats(cb: CallbackQuery, session) -> None:
    s = StatsRepository(session)
    users = await s.users_count()
    premium = await s.premium_count()
    scenarios = await s.scenarios_count()
    t_cnt, t_sum = await s.today()
    m_cnt, m_sum = await s.last_30_days()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b>\n"
        f"⭐ Premium: <b>{premium}</b>\n"
        f"🎭 Senariylar: <b>{scenarios}</b>\n\n"
        f"🛒 Bugun: <b>{t_cnt}</b> ta / <b>{int(t_sum)}</b> so'm\n"
        f"📅 30 kun: <b>{m_cnt}</b> ta / <b>{int(m_sum)}</b> so'm"
    )
    await cb.message.edit_text(text, reply_markup=admin_menu_kb())
    await cb.answer()


# ---- Add scenario flow ----
@router.callback_query(F.data == "adm:add")
async def add_start(cb: CallbackQuery, state: FSMContext, session) -> None:
    repo = CatalogRepository(session)
    cats = await repo.list_categories()
    b = InlineKeyboardBuilder()
    for c in cats:
        b.button(text=c.name_uz, callback_data=f"admcat:{c.id}")
    b.adjust(2)
    await cb.message.edit_text("Kategoriyani tanlang:", reply_markup=b.as_markup())
    await state.set_state(AddScenario.category)
    await cb.answer()


@router.callback_query(AddScenario.category, F.data.startswith("admcat:"))
async def add_category(cb: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(category_id=int(cb.data.split(":")[1]))
    await cb.message.edit_text("Senariy nomini yuboring:")
    await state.set_state(AddScenario.title)
    await cb.answer()


@router.message(AddScenario.title, F.text)
async def add_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await message.answer("Qisqacha tavsifni yuboring (yoki '-'):")
    await state.set_state(AddScenario.description)


@router.message(AddScenario.description, F.text)
async def add_desc(message: Message, state: FSMContext) -> None:
    desc = None if message.text.strip() == "-" else message.text.strip()
    await state.update_data(description=desc)
    await message.answer("Narxini yuboring (so'mda, faqat raqam):")
    await state.set_state(AddScenario.price)


@router.message(AddScenario.price, F.text)
async def add_price(message: Message, state: FSMContext) -> None:
    try:
        price = float(message.text.strip().replace(" ", ""))
    except ValueError:
        await message.answer("❌ Raqam yuboring.")
        return
    await state.update_data(price=price)
    await message.answer("📄 Senariy faylini yuboring (DOCX yoki PDF document):")
    await state.set_state(AddScenario.file)


@router.message(AddScenario.file, F.document)
async def add_file(message: Message, state: FSMContext) -> None:
    doc = message.document
    fmt = FileFormat.pdf if (doc.file_name or "").lower().endswith(".pdf") else FileFormat.docx
    await state.update_data(file_id=doc.file_id, file_format=fmt.value)
    await message.answer("🖼 Muqova rasmini yuboring (yoki /skip):")
    await state.set_state(AddScenario.cover)


@router.message(AddScenario.cover, Command("skip"))
async def cover_skip(message: Message, state: FSMContext, session) -> None:
    await _finish(message, state, session, cover_file_id=None)


@router.message(AddScenario.cover, F.photo)
async def add_cover(message: Message, state: FSMContext, session) -> None:
    await _finish(message, state, session, cover_file_id=message.photo[-1].file_id)


async def _finish(message, state, session, cover_file_id) -> None:
    data = await state.get_data()
    repo = CatalogRepository(session)
    sc = await repo.create_scenario(
        category_id=data["category_id"],
        title=data["title"],
        description=data.get("description"),
        keywords=(data["title"]).lower(),
        price=data["price"],
        file_format=FileFormat(data["file_format"]),
        file_id=data["file_id"],
        cover_file_id=cover_file_id,
        rating=5.0,
    )
    await state.clear()
    from app.services.audit import log_action

    await log_action(
        session, message.from_user.id, "scenario_add", f"id={sc.id} {sc.title}"
    )
    await message.answer(
        f"✅ Qo'shildi: <b>{sc.title}</b> (ID {sc.id})",
        reply_markup=admin_menu_kb(),
    )
