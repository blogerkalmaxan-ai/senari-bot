from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.locales import t
from app.models import Category, Scenario
from app.repositories.catalog import PAGE_SIZE


def cat_name(cat: Category, lang: str) -> str:
    return getattr(cat, f"name_{lang}", None) or cat.name_uz


def categories_kb(categories: list[Category], lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for c in categories:
        b.button(text=cat_name(c, lang), callback_data=f"cat:{c.id}:0")
    b.button(text=t("back_btn", lang), callback_data="menu:home")
    b.adjust(2)
    return b.as_markup()


def scenario_list_kb(
    scenarios: list[Scenario], cat_id: int, page: int, total: int, lang: str
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for s in scenarios:
        b.button(text=f"{s.title} — {int(s.price)}", callback_data=f"sc:{s.id}")
    b.adjust(1)

    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(text="◀️", callback_data=f"cat:{cat_id}:{page-1}")
        )
    last_page = (total - 1) // PAGE_SIZE if total else 0
    nav.append(
        InlineKeyboardButton(
            text=f"{t('pages_label', lang)} {page+1}/{last_page+1}",
            callback_data="noop",
        )
    )
    if page < last_page:
        nav.append(
            InlineKeyboardButton(text="▶️", callback_data=f"cat:{cat_id}:{page+1}")
        )
    if nav:
        b.row(*nav)
    b.row(InlineKeyboardButton(text=t("back_btn", lang), callback_data="menu:catalog"))
    return b.as_markup()


def scenario_card_kb(scenario: Scenario, lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⭐ Stars bilan", callback_data=f"buy:{scenario.id}")
    b.button(text="💳 Karta orqali", callback_data=f"card:{scenario.id}")
    b.button(
        text=t("back_btn", lang),
        callback_data=f"cat:{scenario.category_id}:0",
    )
    b.adjust(1)
    return b.as_markup()
