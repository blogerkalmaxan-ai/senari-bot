from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.locales import t


def menu_labels(lang: str) -> dict:
    return {
        "catalog": t("m_catalog", lang),
        "search": t("m_search", lang),
        "purchases": t("m_purchases", lang),
        "premium": t("m_premium", lang),
        "help": t("m_help", lang),
        "profile": t("m_profile", lang),
    }


def reply_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    lb = menu_labels(lang)
    b = ReplyKeyboardBuilder()
    b.button(text=lb["catalog"])
    b.button(text=lb["search"])
    b.button(text=lb["purchases"])
    b.button(text=lb["premium"])
    b.button(text=lb["help"])
    b.button(text=lb["profile"])
    b.adjust(1, 2, 2, 1)
    return b.as_markup(resize_keyboard=True, is_persistent=True)


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("share_phone_btn", lang), request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def skip_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("skip_btn", lang))]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("m_catalog", lang), callback_data="menu:catalog")
    b.button(text=t("m_search", lang), callback_data="menu:search")
    b.button(text=t("m_purchases", lang), callback_data="menu:purchases")
    b.button(text=t("m_premium", lang), callback_data="menu:premium")
    b.button(text=t("m_help", lang), callback_data="menu:help")
    b.button(text=t("m_profile", lang), callback_data="menu:profile")
    b.adjust(1)
    return b.as_markup()
