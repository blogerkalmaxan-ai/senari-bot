from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.keyboards.common import lang_kb, main_menu_kb, phone_kb, skip_kb
from app.locales import t
from app.models import User
from app.repositories.user import UserRepository
from app.states.registration import Register

router = Router()


async def show_main_menu(message: Message, lang: str) -> None:
    await message.answer(t("main_menu", lang), reply_markup=ReplyKeyboardRemove())
    await message.answer("👇", reply_markup=main_menu_kb(lang))


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, db_user: User | None
) -> None:
    await state.clear()
    if db_user and db_user.phone:
        await show_main_menu(message, db_user.lang)
        return
    await message.answer(t("choose_lang"), reply_markup=lang_kb())
    await state.set_state(Register.lang)


@router.callback_query(Register.lang, F.data.startswith("lang:"))
async def pick_lang(
    cb: CallbackQuery, state: FSMContext, users: UserRepository, db_user: User | None
) -> None:
    lang = cb.data.split(":")[1]
    if not db_user:
        db_user = await users.create(tg_id=cb.from_user.id, lang=lang)
    else:
        await users.update(db_user, lang=lang)
    await state.update_data(lang=lang)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("ask_name", lang))
    await state.set_state(Register.name)
    await cb.answer()


@router.message(Register.name, F.text)
async def get_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(name=message.text.strip()[:128])
    await message.answer(t("ask_phone", lang), reply_markup=phone_kb(lang))
    await state.set_state(Register.phone)


@router.message(Register.phone, F.contact)
async def get_phone(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(phone=message.contact.phone_number)
    await message.answer(t("ask_region", lang), reply_markup=skip_kb(lang))
    await state.set_state(Register.region)


@router.message(Register.region, F.text)
async def get_region(
    message: Message, state: FSMContext, users: UserRepository, db_user: User
) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    region = None if message.text == t("skip_btn", lang) else message.text.strip()[:64]
    await users.update(
        db_user,
        name=data.get("name"),
        phone=data.get("phone"),
        region=region,
        lang=lang,
    )
    await message.answer(t("registered", lang, name=data.get("name", "")))
    await show_main_menu(message, lang)
    await state.clear()
