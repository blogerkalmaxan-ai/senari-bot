from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.keyboards.catalog import (
    cat_name,
    categories_kb,
    scenario_card_kb,
    scenario_list_kb,
)
from app.keyboards.common import main_menu_kb
from app.locales import t
from app.models import User
from app.repositories.catalog import CatalogRepository

router = Router()


class Search(StatesGroup):
    query = State()


def _lang(db_user: User | None) -> str:
    return db_user.lang if db_user else "uz"


def render_card(s, cat_name_str: str, lang: str) -> str:
    parts = [f"<b>{s.title}</b>"]
    if s.description:
        parts.append(s.description)
    parts.append("")
    parts.append(f"🏷 {cat_name_str}")
    if s.pages:
        parts.append(f"{t('card_pages', lang)}: {s.pages}")
    parts.append(f"📁 {s.file_format.value.upper()}")
    parts.append(f"{t('card_rating', lang)}: {s.rating} / 5")
    parts.append(f"{t('card_price', lang)}: <b>{int(s.price)} so'm</b>")
    return "\n".join(parts)


@router.callback_query(F.data == "menu:home")
async def back_home(cb: CallbackQuery, db_user: User | None) -> None:
    lang = _lang(db_user)
    await cb.message.edit_text(t("main_menu", lang), reply_markup=main_menu_kb(lang))
    await cb.answer()


@router.callback_query(F.data == "menu:catalog")
async def open_catalog(
    cb: CallbackQuery, session, db_user: User | None
) -> None:
    lang = _lang(db_user)
    repo = CatalogRepository(session)
    cats = await repo.list_categories()
    await cb.message.edit_text(
        t("categories_title", lang), reply_markup=categories_kb(cats, lang)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("cat:"))
async def open_category(cb: CallbackQuery, session, db_user: User | None) -> None:
    lang = _lang(db_user)
    _, cat_id, page = cb.data.split(":")
    cat_id, page = int(cat_id), int(page)
    repo = CatalogRepository(session)
    scenarios, total = await repo.list_by_category(cat_id, page)
    cat = await repo.get_category(cat_id)
    title = cat_name(cat, lang) if cat else ""
    if not scenarios:
        await cb.answer(t("no_scenarios", lang), show_alert=True)
        return
    await cb.message.edit_text(
        f"🎭 <b>{title}</b>",
        reply_markup=scenario_list_kb(scenarios, cat_id, page, total, lang),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("sc:"))
async def open_scenario(cb: CallbackQuery, session, db_user: User | None) -> None:
    lang = _lang(db_user)
    sc_id = int(cb.data.split(":")[1])
    repo = CatalogRepository(session)
    s = await repo.get_scenario(sc_id)
    if not s:
        await cb.answer("❌", show_alert=True)
        return
    cat = await repo.get_category(s.category_id)
    text = render_card(s, cat_name(cat, lang) if cat else "", lang)
    kb = scenario_card_kb(s, lang)
    if s.cover_file_id:
        await cb.message.answer_photo(s.cover_file_id, caption=text, reply_markup=kb)
        await cb.answer()
    else:
        await cb.message.edit_text(text, reply_markup=kb)
        await cb.answer()


@router.callback_query(F.data == "menu:search")
async def ask_search(cb: CallbackQuery, state: FSMContext, db_user: User | None) -> None:
    lang = _lang(db_user)
    await cb.message.answer(t("search_prompt", lang))
    await state.set_state(Search.query)
    await cb.answer()


@router.message(Search.query, F.text)
async def do_search(
    message: Message, state: FSMContext, session, db_user: User | None
) -> None:
    lang = _lang(db_user)
    repo = CatalogRepository(session)
    scenarios, total = await repo.search(message.text.strip(), 0)
    await state.clear()
    if not scenarios:
        await message.answer(t("search_empty", lang))
        return
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    b = InlineKeyboardBuilder()
    for s in scenarios:
        b.button(text=f"{s.title} — {int(s.price)}", callback_data=f"sc:{s.id}")
    b.adjust(1)
    await message.answer(f"🔍 {total} ta natija:", reply_markup=b.as_markup())


@router.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery) -> None:
    await cb.answer()
